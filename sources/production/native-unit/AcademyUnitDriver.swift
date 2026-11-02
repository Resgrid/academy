import XCTest
import Foundation
import UIKit

// Dedicated test-runner file inbox, never Unit storage or a backend interface.
// All product interaction is through the public XCUI element interface.
@MainActor
final class AcademyUnitDriver: XCTestCase {
    private let app = XCUIApplication(bundleIdentifier: "com.resgrid.unit.development")
    private var credentialsPresent = false
    private var inbox: URL!
    private var stopRequested = false
    private let deniedLabels = Set(["Complete", "Cancel count", "Submit", "Save", "Submit report", "Submit checklist", "Finalize", "Sign as crew boss", "Record agency signature", "Record movement", "Issue", "Return", "Logout", "Sign Out", "Allow", "Always Allow", "Allow While Using App", "Confirm Location", "Set Location"])

    private enum DriverError: Error { case guarded(String) }

    private func write(_ value: [String: Any], name: String) throws {
        let data = try JSONSerialization.data(withJSONObject: value, options: [.prettyPrinted, .sortedKeys])
        try data.write(to: inbox.appendingPathComponent(name), options: .atomic)
    }

    private func element(_ request: [String: Any]) throws -> XCUIElement {
        guard let label = request["label"] as? String, !label.isEmpty else { throw DriverError.guarded("Missing actual UI label/identifier") }
        let kind = request["element_type"] as? String ?? "button"
        let query: XCUIElementQuery
        switch kind {
        case "button": query = app.buttons
        case "staticText": query = app.staticTexts
        case "textField": query = app.textFields
        case "secureTextField": query = app.secureTextFields
        case "other": query = app.otherElements
        default: throw DriverError.guarded("Unsupported UI selector type")
        }
        // XCTest identifier matching throws an Objective-C exception above 128
        // characters. A literal predicate supports actual long warning labels
        // without truncation, regex interpretation or coordinate fallbacks.
        let exact = NSPredicate(format: "identifier == %@ OR label == %@", label, label)
        let candidates = query.matching(exact).allElementsBoundByIndex.filter { $0.exists && $0.isHittable }
        guard candidates.count == 1 else { throw DriverError.guarded("Actual UI target is missing, obscured or ambiguous") }
        return candidates[0]
    }

    private func privacySafe() -> Bool {
        guard app.state == .runningForeground else { return false }
        let authenticationFields = app.textFields.allElementsBoundByIndex.filter {
            ($0.placeholderValue ?? "").lowercased().contains("username")
        }
        if credentialsPresent && app.secureTextFields.count == 0 && authenticationFields.isEmpty { credentialsPresent = false }
        if credentialsPresent { return false }
        for field in authenticationFields {
            let value = field.value as? String ?? ""
            if !value.isEmpty && value != (field.placeholderValue ?? "") { return false }
        }
        return app.secureTextFields.allElementsBoundByIndex.allSatisfy { field in
            guard field.exists else { return true }
            let value = field.value as? String ?? ""
            let placeholder = field.placeholderValue ?? ""
            return value.isEmpty || value == placeholder
        }
    }

    private func inspect() throws -> [String: Any] {
        guard app.state == .runningForeground else { throw DriverError.guarded("Unit is not the actual foreground application") }
        guard privacySafe() else { throw DriverError.guarded("Credential form is populated; no capture/tree inspection allowed") }
        let frame = app.frame
        let items = app.descendants(matching: .any).allElementsBoundByIndex.compactMap { element -> [String: Any]? in
            guard element.exists && element.isHittable else { return nil }
            let rectangle = element.frame
            guard !rectangle.isEmpty && frame.contains(rectangle) else { return nil }
            let label = element.label
            let identifier = element.identifier
            guard !label.isEmpty || !identifier.isEmpty else { return nil }
            var row: [String: Any] = ["type": String(describing: element.elementType), "label": label, "identifier": identifier, "hittable": true,
                                     "rect_points": ["x": rectangle.minX, "y": rectangle.minY, "width": rectangle.width, "height": rectangle.height]]
            if element.elementType != .secureTextField, let value = element.value as? String { row["value"] = value }
            if let placeholder = element.placeholderValue { row["placeholder"] = placeholder }
            return row
        }
        return ["bundle_id": "com.resgrid.unit.development", "state": "running_foreground", "coordinate_space": "logical_points",
                "app_frame_points": ["x": frame.minX, "y": frame.minY, "width": frame.width, "height": frame.height],
                "screen_scale": UIScreen.main.scale, "device_orientation": XCUIDevice.shared.orientation.rawValue,
                "elements": items, "source_only": true, "reviewed_visible_labels": false]
    }

    private func signIn(_ request: [String: Any]) throws -> [String: Any] {
        guard app.alerts.count == 0 else { throw DriverError.guarded("A real alert blocks sign-in; inspect it before entering credentials") }
        let privateFile = inbox.appendingPathComponent("credentials.private.json")
        defer { try? FileManager.default.removeItem(at: privateFile) }
        guard let data = try? Data(contentsOf: privateFile),
              let values = try JSONSerialization.jsonObject(with: data) as? [String: String],
              let username = values["username"], let password = values["password"] else { throw DriverError.guarded("Private runner credentials are absent") }
        let usernameField = try element(["label": request["username_label"] as? String ?? "Username", "element_type": "textField"])
        let passwordField = try element(["label": request["password_label"] as? String ?? "Password", "element_type": "secureTextField"])
        let submit = try element(["label": request["submit_label"] as? String ?? "Sign In", "element_type": "button"])
        credentialsPresent = true
        usernameField.tap(); usernameField.typeText(username)
        passwordField.tap(); passwordField.typeText(password)
        submit.tap()
        let deadline = Date().addingTimeInterval(25)
        while Date() < deadline {
            if !usernameField.exists && !passwordField.exists {
                credentialsPresent = false
                return ["status": "credential_form_departed", "success_not_assumed": true, "requires_actual_next_screen_review": true]
            }
            RunLoop.current.run(until: Date().addingTimeInterval(0.25))
        }
        return ["status": "credential_form_still_present", "capture_and_tree_blocked": true]
    }

    private func handle(_ request: [String: Any]) throws -> [String: Any] {
        guard let action = request["action"] as? String else { throw DriverError.guarded("Missing UI action") }
        if action != "stop" && action != "capture_guard" && action != "open_local_project_confirmation" && action != "deny_own_location_permission" && app.state != .runningForeground {
            throw DriverError.guarded("Unit is not the actual foreground application; no element query or interaction attempted")
        }
        switch action {
        case "deny_own_location_permission":
            guard !credentialsPresent else { throw DriverError.guarded("No system action while credentials are present") }
            let system = XCUIApplication(bundleIdentifier: "com.apple.springboard")
            let alert = system.alerts.firstMatch
            guard alert.exists,
                  alert.staticTexts.matching(NSPredicate(format: "label CONTAINS %@ AND label CONTAINS %@", "Resgrid Unit", "location")).count > 0,
                  alert.buttons["Allow Once"].exists,
                  alert.buttons["Allow While Using App"].exists else { throw DriverError.guarded("Exact own-app location permission request is absent") }
            let denials = alert.buttons.matching(NSPredicate(format: "label == %@ OR label == %@", "Don’t Allow", "Don't Allow")).allElementsBoundByIndex.filter { $0.exists && $0.isHittable }
            guard denials.count == 1 else { throw DriverError.guarded("Unique normal location denial button is absent") }
            denials[0].tap()
            return ["status": "own_location_permission_denied", "permission_granted": false, "gps_exercised": false]
        case "open_local_project_confirmation":
            guard !credentialsPresent else { throw DriverError.guarded("Credentials prevent a system app-opening action") }
            let system = XCUIApplication(bundleIdentifier: "com.apple.springboard")
            let alert = system.alerts.firstMatch
            guard alert.exists,
                  alert.staticTexts.matching(NSPredicate(format: "label CONTAINS %@ AND label CONTAINS %@", "Open in", "Resgrid Unit")).count == 1,
                  alert.buttons.count == 2, alert.buttons["Cancel"].exists,
                  alert.buttons["Open"].exists && alert.buttons["Open"].isHittable else {
                throw DriverError.guarded("Exact ordinary Resgrid Unit opening confirmation is absent; no other system alert is touched")
            }
            alert.buttons["Open"].tap()
            return ["status": "ordinary_local_app_open_confirmed", "privacy_or_account_permission_granted": false]
        case "inspect": return try inspect()
        case "tap":
            guard privacySafe(), let label = request["label"] as? String, !deniedLabels.contains(label), app.alerts.count == 0 else { throw DriverError.guarded("Mutation/permission/alert action is not allowed by this capture harness") }
            let target = try element(request)
            // A test identifier must not alias a prohibited visible action.
            guard !deniedLabels.contains(target.label) else { throw DriverError.guarded("Actual target action requires a separately scoped handler") }
            let rectangle = target.frame
            let actual: [String: Any] = ["accessible_label": target.label, "identifier": target.identifier,
                                        "type": String(describing: target.elementType),
                                        "rect_points": ["x": rectangle.minX, "y": rectangle.minY, "width": rectangle.width, "height": rectangle.height]]
            target.tap()
            return ["status": "ordinary_ui_tap_performed", "target": label, "actual_control_before_tap": actual]
        case "scroll":
            guard privacySafe(), app.alerts.count == 0 else { throw DriverError.guarded("Unsafe scroll context") }
            switch request["direction"] as? String {
            case "up": app.swipeUp()
            case "down": app.swipeDown()
            default: throw DriverError.guarded("Unsupported scroll direction")
            }
            return ["status": "ordinary_ui_scroll_performed"]
        case "landscape":
            guard privacySafe() else { throw DriverError.guarded("Credential privacy guard") }
            XCUIDevice.shared.orientation = .landscapeLeft
            return ["status": "owned_device_landscape_requested"]
        case "configure_local_training_server":
            guard privacySafe(), app.alerts.count == 0,
                  app.staticTexts.matching(NSPredicate(format: "label BEGINSWITH %@", "Note: This is the URL of the Resgrid API.")).count > 0,
                  app.buttons["Cancel"].exists else { throw DriverError.guarded("Actual empty Server URL sheet is required") }
            let local = "http://127.0.0.1:18967"
            let fields = app.textFields.matching(NSPredicate(format: "placeholderValue == %@", "Enter Resgrid API URL (e.g., https://api.resgrid.com)")).allElementsBoundByIndex.filter { $0.exists && $0.isHittable }
            guard fields.count == 1 else { throw DriverError.guarded("Unique actual Server URL field is absent") }
            let field = fields[0]
            let initial = field.value as? String ?? ""
            guard initial.isEmpty || initial == field.placeholderValue else { throw DriverError.guarded("Preserve any existing nonempty server setting") }
            field.tap(); field.typeText(local)
            guard field.value as? String == local else { throw DriverError.guarded("Visible local URL readback differs; nothing saved") }
            let save = try element(["label": "Save", "element_type": "button"])
            save.tap()
            return ["status": "ordinary_local_server_form_saved", "endpoint": local, "account_security_changed": false]
        case "signin": return try signIn(request)
        case "show_inventory_complete_confirmation":
            guard privacySafe(), app.alerts.count == 0,
                  app.staticTexts.matching(NSPredicate(format: "label CONTAINS %@", "counted")).count > 0 else { throw DriverError.guarded("Actual inventory count context is not established") }
            let button = app.buttons["Complete"]
            guard button.exists && button.isHittable && button.isEnabled else { throw DriverError.guarded("Complete confirmation launcher is unavailable") }
            button.tap()
            guard app.alerts.firstMatch.waitForExistence(timeout: 5) else { throw DriverError.guarded("No actual native confirmation appeared") }
            return ["status": "actual_native_confirmation_open", "no_confirmation_button_pressed": true]
        case "confirm_matching_inventory_alert":
            guard privacySafe(), app.alerts.count == 1 else { throw DriverError.guarded("One actual native inventory confirmation is required") }
            let alert = app.alerts.firstMatch
            guard alert.label == "Complete count?",
                  alert.staticTexts["Everything matches what was expected."].exists,
                  alert.buttons.count == 2, alert.buttons["Cancel"].exists,
                  alert.buttons["Complete"].exists && alert.buttons["Complete"].isHittable else {
                throw DriverError.guarded("Only the actual zero-difference Complete count confirmation is authorized")
            }
            alert.buttons["Complete"].tap()
            return ["status": "ordinary_zero_difference_count_confirmation_submitted", "success_not_assumed": true, "requires_fresh_history_and_reopen_readback": true]
        case "dismiss_inventory_confirmation":
            guard privacySafe(), app.alerts.count == 1, app.alerts.firstMatch.buttons["Cancel"].exists else { throw DriverError.guarded("Expected safe cancel-confirmation button is absent") }
            app.alerts.firstMatch.buttons["Cancel"].tap()
            return ["status": "confirmation_dismissed_without_count_completion"]
        case "capture_guard": return ["capture_allowed": privacySafe() && app.state == .runningForeground, "unit_foreground": app.state == .runningForeground]
        case "stop": stopRequested = true; return ["status": "driver_stopping_without_data_reset"]
        default: throw DriverError.guarded("Action is outside the ordinary UI allowlist")
        }
    }

    func testNormalUICommandLoop() throws {
        continueAfterFailure = false
        let process = ProcessInfo.processInfo.environment
        guard let expected = process["ACADEMY_SIMULATOR_UDID"], expected == process["SIMULATOR_UDID"],
              process["ACADEMY_DEDICATED_SESSION"] == "true" else { throw XCTSkip("No exact dedicated simulator binding; no Unit interaction") }
        inbox = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("AcademyDriver", isDirectory: true)
        try FileManager.default.createDirectory(at: inbox, withIntermediateDirectories: true)
        // XCTest setup may stop its target. Wait for the host to open the normal
        // explicit local dev-client URL after this runner is ready; never launch
        // Unit against a default or somebody else's Metro project.
        if app.state == .runningForeground || app.state == .runningBackground { app.activate() }
        try write(["ready": true, "simulator_udid": expected, "bundle_id": "com.resgrid.unit.development", "normal_ui_only": true,
                   "private_runner_documents": inbox.path, "no_automatic_capture": true], name: "ready.json")
        let deadline = Date().addingTimeInterval(3600)
        let requestURL = inbox.appendingPathComponent("request.json")
        while !stopRequested && Date() < deadline {
            if let data = try? Data(contentsOf: requestURL), let request = try? JSONSerialization.jsonObject(with: data) as? [String: Any], let id = request["id"] as? String {
                try? FileManager.default.removeItem(at: requestURL)
                var response: [String: Any] = ["id": id, "at": ISO8601DateFormatter().string(from: Date()), "source_only": true]
                do { response["result"] = try handle(request); response["ok"] = true }
                catch { response["ok"] = false; response["error"] = String(describing: error) }
                try write(response, name: "response-" + id + ".json")
            }
            RunLoop.current.run(until: Date().addingTimeInterval(0.2))
        }
    }
}
