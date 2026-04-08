export const load = async ({ parent, params }) => {
  const parentData = await parent()
  return {
    comun: parentData.comun ?? null,
    slug: params.slug,
  }
}
