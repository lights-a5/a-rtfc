export const client_id = '<<<<<client_id>>>>>'
export const serverURL = '<<<<<server_url>>>>>'
export const wsURL = '<<<<<websocket_url>>>>>'

import * as Sentry from '@sentry/electron'

export function captureMessage(m, extra) {
  Sentry.getDefaultHub().withScope(() => {
    Sentry.getDefaultHub().configureScope(scope => {
      for (let [k, v] of Object.entries(extra || {})) {
        scope.setExtra(k, v)
      }
      Sentry.captureMessage(m)
    })
  })
}

export function captureException(e, extra) {
  Sentry.getDefaultHub().withScope(() => {
    Sentry.getDefaultHub().configureScope(scope => {
      for (let [k, v] of Object.entries(extra || {})) {
        scope.setExtra(k, v)
      }
      Sentry.captureException(e)
    })
  })
}
