import { env } from '$env/dynamic/public'
import type { Theme, ThemeColors } from './colors'

export function getDefaultColors(): ThemeColors {
  return env.PUBLIC_THEME
    ? JSON.parse(env.PUBLIC_THEME)
    : {
        slate: {
          25: '252 253 254',
          50: '242 242 242',
          100: '241 245 249',
          200: '226 232 240',
          300: '203 213 225',
          400: '148 163 184',
          500: '100 116 139',
          600: '71 85 105',
          700: '51 65 85',
          800: '30 41 59',
          900: '15 23 42',
          950: '2 6 23',
        },
        zinc: {
          50: '251 253 255',
          100: '246 247 249',
          300: '217 221 226',
          400: '171 177 188',
          500: '127 133 146',
          600: '95 104 117',
          700: '75 84 99',
          800: '42 50 63',
          900: '32 37 50',
          925: '28 32 43',
          950: '23 27 36',
        },
        primary: {
          100: '229 240 255',
          900: '10 132 255',
        },
        other: {
          black: '0 0 0',
          white: '255 255 255',
        },
      }
}

export function getDefaultTheme(): Theme {
  return {
    id: 0,
    colors: getDefaultColors(),
    name: 'Default',
  }
}
