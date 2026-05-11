import sanitizeHtml from 'sanitize-html'
import { getSafeUrl } from './url'

const ALLOWED_IFRAME_PREFIXES = [
  'https://t.me/',
  'https://www.openstreetmap.org/export/embed.html',
  'https://open.spotify.com/embed/',
  'https://w.soundcloud.com/player/',
  'https://music.yandex.ru/iframe/',
  'https://music.yandex.com/iframe/',
]

const isAllowedIframeSrc = (value: unknown) => {
  const url = getSafeUrl(value, { allowRelative: false })
  return Boolean(url && ALLOWED_IFRAME_PREFIXES.some((prefix) => url.startsWith(prefix)))
}

const sanitizeSrcSet = (value: unknown) => {
  return String(value ?? '')
    .split(',')
    .map((candidate) => {
      const parts = candidate.trim().split(/\s+/)
      const url = getSafeUrl(parts[0], { allowRelative: true, allowDataImage: true })
      if (!url) return ''
      return [url, ...parts.slice(1)].join(' ')
    })
    .filter(Boolean)
    .join(', ')
}

export const sanitizePostHtml = (html: string) =>
  sanitizeHtml(String(html ?? ''), {
    allowedTags: [
      'p',
      'h1',
      'h2',
      'h3',
      'h4',
      'h5',
      'h6',
      'nav',
      'span',
      'b',
      'i',
      'em',
      'strong',
      'a',
      'br',
      'ul',
      'ol',
      'li',
      'img',
      'audio',
      'source',
      'progress',
      'table',
      'thead',
      'tbody',
      'tr',
      'td',
      'th',
      'figure',
      'figcaption',
      'input',
      'blockquote',
      'footer',
      'div',
      'iframe',
      'pre',
      'code',
    ],
    allowedAttributes: {
      a: ['href', 'target', 'rel', 'title', 'class', 'id', 'aria-label'],
      audio: ['src', 'controls', 'preload', 'class'],
      source: ['src', 'type'],
      img: [
        'src',
        'srcset',
        'sizes',
        'loading',
        'fetchpriority',
        'alt',
        'width',
        'height',
        'class',
        'title',
        'data-expandable-image',
        'data-expandable-src',
      ],
      iframe: ['src', 'allow', 'allowfullscreen', 'frameborder', 'referrerpolicy', 'loading', 'class'],
      input: ['type', 'value', 'max', 'class', 'data-option-index'],
      '*': [
        'class',
        'id',
        'role',
        'tabindex',
        'aria-expanded',
        'aria-label',
        'hidden',
        'data-compare-position',
        'data-poll-multiple',
        'data-poll-closed',
        'data-poll-locked',
        'data-poll-id',
        'data-rating-block-id',
        'data-rating-value',
        'data-music-provider',
        'data-spoiler-open',
        'data-post-link-id',
        'data-post-link-needs-hydration',
        'data-post-link-hydrated',
        'data-post-link-title',
        'data-post-link-text',
        'data-post-link-image',
        'data-glossary-term',
        'data-glossary-slug',
        'data-glossary-definition',
      ],
    },
    allowedSchemes: ['http', 'https', 'mailto'],
    allowedSchemesByTag: {
      img: ['http', 'https', 'data'],
      source: ['http', 'https'],
      audio: ['http', 'https'],
      iframe: ['http', 'https'],
    },
    parser: {
      lowerCaseTags: true,
    },
    parseStyleAttributes: false,
    transformTags: {
      a: (tagName, attribs) => {
        const href = getSafeUrl(attribs.href, {
          allowedProtocols: ['http:', 'https:', 'mailto:'],
          allowRelative: true,
        })
        const relParts = new Set(
          String(attribs.rel || '')
            .split(/\s+/)
            .filter(Boolean)
        )
        if (href?.includes('t.me/')) {
          relParts.add('nofollow')
          relParts.add('noopener')
        }
        const { href: _href, rel: _rel, ...safeAttribs } = attribs
        return {
          tagName,
          attribs: {
            ...safeAttribs,
            ...(href ? { href } : {}),
            ...(relParts.size ? { rel: Array.from(relParts).join(' ') } : {}),
          },
        }
      },
      img: (tagName, attribs) => {
        const src = getSafeUrl(attribs.src, { allowRelative: true, allowDataImage: true })
        const expandedSrc = getSafeUrl(attribs['data-expandable-src'], {
          allowRelative: true,
          allowDataImage: true,
        })
        const srcset = sanitizeSrcSet(attribs.srcset)
        const {
          src: _src,
          srcset: _srcset,
          'data-expandable-src': _expandedSrc,
          ...safeAttribs
        } = attribs
        return {
          tagName,
          attribs: {
            ...safeAttribs,
            ...(src ? { src } : {}),
            ...(expandedSrc ? { 'data-expandable-src': expandedSrc } : {}),
            ...(srcset ? { srcset } : {}),
          },
        }
      },
      source: (tagName, attribs) => {
        const src = getSafeUrl(attribs.src, { allowRelative: true })
        const { src: _src, ...safeAttribs } = attribs
        return { tagName, attribs: { ...safeAttribs, ...(src ? { src } : {}) } }
      },
      audio: (tagName, attribs) => {
        const src = getSafeUrl(attribs.src, { allowRelative: true })
        const { src: _src, ...safeAttribs } = attribs
        return { tagName, attribs: { ...safeAttribs, ...(src ? { src } : {}) } }
      },
    },
    exclusiveFilter: (frame) => frame.tag === 'iframe' && !isAllowedIframeSrc(frame.attribs.src),
  })
