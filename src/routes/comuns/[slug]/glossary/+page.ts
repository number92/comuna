import { error } from '@sveltejs/kit'

export const load = async ({ parent }) => {
  const parentData = await parent()
  const comun = parentData.comun ?? null
  if (!comun?.glossary_enabled) {
    throw error(404, 'Глоссарий не включен')
  }
  return {
    comun,
  }
}
