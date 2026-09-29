{{- define "app.name" -}}{{ .Chart.Name }}{{- end }}
{{- define "app.fullname" -}}{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}{{- end }}
{{- define "app.labels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
{{- define "app.env" -}}
- name: APP_OFFLINE
  value: {{ ternary "1" "0" .Values.offline | quote }}
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ default (printf "%s-db" (include "app.fullname" .)) .Values.database.existingSecret }}
      key: DATABASE_URL
{{- if not .Values.offline }}
- name: ANTHROPIC_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "app.fullname" . }}-secrets
      key: ANTHROPIC_API_KEY
      optional: true
{{- end }}
{{- end }}
