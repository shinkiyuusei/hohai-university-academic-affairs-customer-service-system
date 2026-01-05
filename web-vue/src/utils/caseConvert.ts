// 简单的对象键名大小写转换工具
// 将后端返回的下划线命名转换成前端使用的驼峰命名，或反向转换

type PlainObject = Record<string, unknown>

const isPlainObject = (value: unknown): value is PlainObject => {
  if (!value || typeof value !== 'object') {
    return false
  }

  const prototype = Object.getPrototypeOf(value)
  return prototype === Object.prototype || prototype === null
}

const toCamelKey = (key: string) =>
  key.replace(/_([a-z])/g, (_, char: string) => char.toUpperCase())

const toSnakeKey = (key: string) =>
  key.replace(/([A-Z])/g, '_$1').toLowerCase()

const transformKeys = (input: unknown, transform: (key: string) => string): unknown => {
  if (Array.isArray(input)) {
    return input.map((item) => transformKeys(item, transform))
  }

  if (isPlainObject(input)) {
    const result: PlainObject = {}
    Object.entries(input).forEach(([key, value]) => {
      result[transform(key)] = transformKeys(value, transform)
    })
    return result
  }

  return input
}

export const keysToCamel = <T>(input: unknown): T => transformKeys(input, toCamelKey) as T
export const keysToSnake = <T>(input: unknown): T => transformKeys(input, toSnakeKey) as T
