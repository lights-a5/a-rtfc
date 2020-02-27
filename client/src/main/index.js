import { app, BrowserWindow, ipcMain } from 'electron'
import { init } from '@sentry/electron'
import _ from 'lodash'
import path from 'path'
import storeFactory from './store'
import tailLog from './tail'
import publish from './publisher'
import Parser from './parser'

init({
  dsn: 'https://0680c2cdbb4c4cdb820e9c9784fc5dc8@sentry.io/1268077',
  release: `A-RTFC-${app.getVersion()}`,
  captureUnhandledRejections: true,
  autoBreadcrumbs: true,
})

let mainWindow, store, parser
const winURL = process.env.NODE_ENV === 'development' ? `http://localhost:9080` : `file://${__dirname}/index.html`
const logPath = process.env.ARENA_LOG_PATH ? process.env.ARENA_LOG_PATH : path.join(app.getPath('userData'), '..', '..', 'LocalLow', 'Wizards of the Coast', 'MTGA', 'output_log.txt')

function createWindow() {
  mainWindow = new BrowserWindow({
    useContentSize: true,
    frame: false,
    // Not sure how to make this not break the build yet :(
    // webPreferences: {
    //   nodeIntegration: false,
    //   contextIsolation: true,
    //   preload: undefined,
    // },
    title: 'Arena: Read the Field Clearly',
    backgroundColor: '#303030',
    show: false,
    ...store.state.windowOptions,
  })

  mainWindow.loadURL(winURL + store.state.windowOptions.anchor)

  mainWindow.once('ready-to-show', () => {
    process.env.NODE_ENV === 'development' && mainWindow.webContents.toggleDevTools()
    mainWindow.show()
    process.env.NODE_ENV === 'development' && mainWindow.webContents.toggleDevTools()
  })
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  let updateWindowOptions = _.debounce(() => {
    store.commit('windowOptions', [mainWindow.getBounds(), mainWindow.webContents.getURL()])
  }, 100)
  mainWindow.on('move', updateWindowOptions)
  mainWindow.on('resize', updateWindowOptions)
  mainWindow.webContents.on('did-navigate-in-page', updateWindowOptions)
}

app.on('ready', async () => {
  store = storeFactory(app.getPath('userData'), ipcMain)
  parser = new Parser(store)
  tailLog(store, logPath, parser.parse.bind(parser))
  publish(store)
  createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

app.on('will-quit', async e => {
  if (store && store.state.status.extactive) {
    e.preventDefault()
    await store.dispatch('disableExtension')
    app.quit()
  }
})