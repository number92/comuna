import type { BackendTopAuthorPeriod } from '$lib/api/backend'

export const authorRatingHref = '/authors/rating'

export const topAuthorPeriodOptions: Array<{
  value: BackendTopAuthorPeriod
  label: string
}> = [
  { value: 'week', label: 'За неделю' },
  { value: 'month', label: 'За месяц' },
  { value: 'all', label: 'За все время' },
]

export const topAuthorPeriodTitleMap: Record<BackendTopAuthorPeriod, string> = {
  week: 'за неделю',
  month: 'за месяц',
  all: 'за все время',
}

export const topAuthorRatingLabelMap: Record<BackendTopAuthorPeriod, string> = {
  week: 'Рейтинг за 7 дней',
  month: 'Рейтинг за 30 дней',
  all: 'Рейтинг за все время',
}

export const topAuthorHeroRatingLabelMap: Record<BackendTopAuthorPeriod, string> = {
  week: 'Рейтинг автора',
  month: 'Рейтинг автора',
  all: 'Рейтинг автора',
}

export const formatTopAuthorNumber = (value: number | undefined) => {
  if (!value && value !== 0) return '0'
  return value.toLocaleString('ru-RU')
}

export const buildTopAuthorsPeriodHref = (period: BackendTopAuthorPeriod) => {
  const params = new URLSearchParams()
  if (period !== 'month') {
    params.set('period', period)
  }
  const query = params.toString()
  return query ? `${authorRatingHref}?${query}` : authorRatingHref
}

export const topAuthorRankBadgeClass = (index: number) => {
  if (index === 0) return 'rank-badge rank-badge--gold'
  if (index === 1) return 'rank-badge rank-badge--silver'
  return 'rank-badge rank-badge--bronze'
}

export const topAuthorHeroCardClass = (index: number) => {
  if (index === 0) return 'hero-card hero-card--gold'
  if (index === 1) return 'hero-card hero-card--silver'
  return 'hero-card hero-card--bronze'
}
