// web_dev/test.setup.js
import { JSDOM } from 'jsdom'

// Only create jsdom if it doesn't already exist
if (typeof document === 'undefined') {
  const dom = new JSDOM('<!doctype html><html><body></body></html>')
  global.window = dom.window
  global.document = dom.window.document
  global.HTMLElement = dom.window.HTMLElement
  global.Node = dom.window.Node
}
