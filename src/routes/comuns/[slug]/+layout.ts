import ComunSidebarInfo from '$lib/components/ui/sidebar/ComunSidebarInfo.svelte'
import { buildComunUrl } from '$lib/api/backend'
import { error } from '@sveltejs/kit'

export const load = async ({ fetch, params, url, depends }) => {
  const slug = params.slug
  depends(`app:comun:${slug}`)

  const comunResponse = await fetch(new URL(buildComunUrl(slug), url.origin).toString())
  if (!comunResponse.ok) {
    if (comunResponse.status === 404) {
      throw error(404, 'Сообщество не найдено')
    }
    throw error(comunResponse.status, 'Не удалось загрузить сообщество')
  }

  const comunPayload = await comunResponse.json()

  return {
    slug,
    comun: comunPayload?.comun ?? null,
    slots: comunPayload?.comun
      ? {
          sidebar: {
            component: ComunSidebarInfo,
            props: {
              comun: comunPayload.comun,
            },
          },
        }
      : undefined,
  }
}
