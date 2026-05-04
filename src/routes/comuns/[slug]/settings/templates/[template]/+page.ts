export const load = async ({ parent, params }) => {
  const parentData = await parent()
  return {
    comun: parentData.comun ?? null,
    hideSidebar: true,
    slug: params.slug,
    template: params.template,
  }
}
