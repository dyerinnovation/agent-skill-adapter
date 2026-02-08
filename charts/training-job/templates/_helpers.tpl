{{/*
Expand the name of the chart.
*/}}
{{- define training-job.name -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix - }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define training-job.fullname -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix - }}
{{- else }}
{{-  := default .Chart.Name .Values.nameOverride }}
{{- if contains  .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix - }}
{{- else }}
{{- printf %s-%s .Release.Name  | trunc 63 | trimSuffix - }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define training-job.chart -}}
{{- printf %s-%s .Chart.Name .Chart.Version | replace + _ | trunc 63 | trimSuffix - }}
{{- end }}

{{/*
Common labels
*/}}
{{- define training-job.labels -}}
helm.sh/chart: {{ include training-job.chart . }}
{{ include training-job.selectorLabels . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define training-job.selectorLabels -}}
app.kubernetes.io/name: {{ include training-job.name . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
