import { useColorScheme } from 'nativewind';
import React, { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { StyleSheet, View } from 'react-native';

import formRenderSource from '@/lib/form-render/form-render-source';
import jquerySource from '@/lib/form-render/jquery-source';

interface CallFormRendererProps {
  formSchemaJson: string;
  onFormDataChange: (formDataJson: string) => void;
  height?: number;
}

function escapeHtmlAttr(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function buildHtml(formSchemaJson: string, isDark: boolean, title: string): string {
  const bg = isDark ? '#171717' : '#ffffff';
  const text = isDark ? '#f3f4f6' : '#111827';
  const border = isDark ? '#404040' : '#d1d5db';
  const inputBg = isDark ? '#262626' : '#f9fafb';
  // Escape the JSON for safe embedding in an HTML attribute — it is never
  // placed inside a <script> block, so it cannot be executed as code.
  const safeSchema = escapeHtmlAttr(formSchemaJson);

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>${title}</title>
<script>${jquerySource}</script>
<script>${formRenderSource}</script>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 8px;
    background-color: ${bg};
    color: ${text};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
  }
  .rendered-form label { display: block; margin-bottom: 4px; font-weight: 500; }
  .rendered-form .form-group { margin-bottom: 12px; }
  .rendered-form input,
  .rendered-form select,
  .rendered-form textarea {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid ${border};
    border-radius: 6px;
    background: ${inputBg};
    color: ${text};
    font-size: 14px;
    outline: none;
  }
  .rendered-form input:focus,
  .rendered-form select:focus,
  .rendered-form textarea:focus {
    border-color: #2563eb;
  }
</style>
</head>
<body>
<!-- Form schema is stored in a data attribute and parsed via JSON.parse —
     it is never interpolated into executable script context. -->
<div id="form-schema-data" data-schema="${safeSchema}" style="display:none"></div>
<form id="callForm" class="rendered-form"></form>
<script>
  $(function() {
    var schemaText = document.getElementById('form-schema-data').getAttribute('data-schema');
    var formData;
    try { formData = JSON.parse(schemaText); } catch(e) { formData = []; }
    $('#callForm').formRender({ formData: formData });

    function sendData() {
      var data = {};
      var formEl = document.getElementById('callForm');
      var fd = new FormData(formEl);
      fd.forEach(function(value, name) {
        if (Object.prototype.hasOwnProperty.call(data, name)) {
          if (!Array.isArray(data[name])) {
            data[name] = [data[name]];
          }
          data[name].push(value);
        } else {
          data[name] = value;
        }
      });
      // Use window.location.origin (same as parent because sandbox uses
      // allow-same-origin) instead of '*' to prevent leaking form data to
      // unintended origins.
      window.parent.postMessage(JSON.stringify(data), window.location.origin);
    }
    document.getElementById('callForm').addEventListener('change', sendData);
    document.getElementById('callForm').addEventListener('input', sendData);
  });
</script>
</body>
</html>`;
}

export const CallFormRenderer: React.FC<CallFormRendererProps> = ({ formSchemaJson, onFormDataChange, height = 400 }) => {
  const { colorScheme } = useColorScheme();
  const { t } = useTranslation();
  const isDark = colorScheme === 'dark';
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const html = buildHtml(formSchemaJson, isDark, t('calls.form.title', 'Call Form'));

  useEffect(() => {
    const handler = (event: MessageEvent) => {
      // Reject messages from unexpected origins (the iframe uses allow-same-origin
      // so legitimate messages will always come from window.location.origin).
      if (event.origin !== window.location.origin) return;
      // Reject messages that do not originate from this specific iframe to
      // prevent other frames or scripts on the page spoofing form data.
      if (event.source !== iframeRef.current?.contentWindow) return;
      if (typeof event.data === 'string') {
        onFormDataChange(event.data);
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [onFormDataChange]);

  return (
    <View style={StyleSheet.flatten([styles.container, { height }, isDark ? styles.containerDark : styles.containerLight])}>
      <iframe ref={iframeRef} srcDoc={html} style={{ width: '100%', height: '100%', border: 'none' }} title={t('calls.form.title', 'Call Form')} sandbox="allow-scripts allow-same-origin" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
  },
  containerDark: { borderColor: '#404040' },
  containerLight: { borderColor: '#e5e7eb' },
});
