import type { Handle } from '@sveltejs/kit';

const PRIORITY_HEAD_TAG_PATTERN =
  /<(?:meta|link)\b[^>]*(?:name="description"|rel="canonical"|property="og:[^"]+"|name="twitter:[^"]+")[^>]*>/gi

const STYLESHEET_LINK_PATTERN = /<link\b[^>]*rel="stylesheet"[^>]*>/i

const prioritizePreviewHeadTags = (html: string) => {
  const headOpenIndex = html.indexOf('<head>')
  const headCloseIndex = html.indexOf('</head>')
  if (headOpenIndex === -1 || headCloseIndex === -1 || headCloseIndex <= headOpenIndex) {
    return html
  }

  const headContentStart = html.indexOf('>', headOpenIndex)
  if (headContentStart === -1) return html

  const headContent = html.slice(headContentStart + 1, headCloseIndex)
  const priorityTags: string[] = []
  const strippedHeadContent = headContent.replace(PRIORITY_HEAD_TAG_PATTERN, (match) => {
    priorityTags.push(match)
    return ''
  })

  if (!priorityTags.length) return html

  const insertionIndex = strippedHeadContent.search(STYLESHEET_LINK_PATTERN)
  if (insertionIndex === -1) return html

  const reorderedHeadContent =
    strippedHeadContent.slice(0, insertionIndex) +
    priorityTags.join('') +
    strippedHeadContent.slice(insertionIndex)

  return (
    html.slice(0, headContentStart + 1) +
    reorderedHeadContent +
    html.slice(headCloseIndex)
  )
}

export const handle: Handle = async ({ event, resolve }) => {
  const response = await resolve(event, {
    transformPageChunk: ({ html }) => prioritizePreviewHeadTags(html),
  });

  // Prevent oversized response headers from SSR preload Link header.
  const headers = new Headers(response.headers);
  headers.delete('link');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
};
