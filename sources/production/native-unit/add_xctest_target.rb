# Adds a public-XCTest-only driver to our generated native project, never original Unit.
require 'json'
require 'fileutils'
require 'xcodeproj'
base = '/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025/native-unit-20261028'
root = File.join(base, 'source', 'ios')
project_path = File.join(root, 'ResgridUnit.xcodeproj')
session = JSON.parse(File.read(File.join(base, 'session.json')))
raise 'Not our dedicated session' unless session['dedicated'] && session['owner'] == 'academy_training' && !session['user_session_reused']
project = Xcodeproj::Project.open(project_path)
app = project.targets.find { |t| t.name == 'ResgridUnit' }
raise 'Generated actual Unit app target missing' unless app
name = 'AcademyUnitUITests'
dir = File.join(root, name)
FileUtils.mkdir_p(dir)
FileUtils.cp(File.join(__dir__, 'AcademyUnitDriver.swift'), File.join(dir, 'AcademyUnitDriver.swift'))
group = project.main_group.groups.find { |g| g.name == name } || project.main_group.new_group(name, name)
reference = group.files.find { |f| f.path == 'AcademyUnitDriver.swift' } || group.new_file('AcademyUnitDriver.swift')
target = project.targets.find { |t| t.name == name } || project.new_target(:ui_test_bundle, name, :ios, '18.1')
target.source_build_phase.add_file_reference(reference, true)
target.add_dependency(app) unless target.dependencies.any? { |d| d.target == app }
project.root_object.attributes['TargetAttributes'] ||= {}
project.root_object.attributes['TargetAttributes'][target.uuid] = { 'TestTargetID' => app.uuid, 'CreatedOnToolsVersion' => '27.1' }
target.build_configurations.each do |configuration|
  configuration.build_settings.merge!({
    'PRODUCT_BUNDLE_IDENTIFIER' => 'com.resgrid.academy.UnitUITests', 'PRODUCT_NAME' => '$(TARGET_NAME)',
    'SWIFT_VERSION' => '5.0', 'GENERATE_INFOPLIST_FILE' => 'YES', 'TEST_TARGET_NAME' => 'ResgridUnit',
    'CODE_SIGNING_ALLOWED' => 'NO', 'ENABLE_TESTING_SEARCH_PATHS' => 'YES', 'TARGETED_DEVICE_FAMILY' => '2',
    'IPHONEOS_DEPLOYMENT_TARGET' => '18.1', 'LD_RUNPATH_SEARCH_PATHS' => ['$(inherited)', '@executable_path/Frameworks', '@loader_path/Frameworks']
  })
end
project.save
scheme = Xcodeproj::XCScheme.new
scheme.add_build_target(app)
scheme.add_build_target(target, false)
scheme.add_test_target(target)
scheme.test_action.build_configuration = 'Debug'
scheme.test_action.should_use_launch_scheme_args_env = false
scheme.test_action.xml_element.attributes['systemAttachmentLifetime'] = 'keepNever'
scheme.test_action.xml_element.attributes['userAttachmentLifetime'] = 'keepNever'
scheme.test_action.xml_element.attributes['preferredScreenCaptureFormat'] = 'screenshot'
scheme.test_action.xml_element.attributes['parallelizable'] = 'NO'
env = Xcodeproj::XCScheme::EnvironmentVariables.new([
 { key: 'ACADEMY_SIMULATOR_UDID', value: session['udid'], enabled: true },
 { key: 'ACADEMY_DEDICATED_SESSION', value: 'true', enabled: true }
])
scheme.test_action.environment_variables = env
scheme.save_as(project_path, 'AcademyUnitRecording', true)
puts JSON.generate({ project: project_path, scheme: 'AcademyUnitRecording', actual_unit_target: app.name, driver_target: target.name, dedicated_simulator: session['udid'], automatic_attachments: 'keepNever' })
