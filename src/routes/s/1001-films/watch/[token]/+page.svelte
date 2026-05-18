<script lang="ts">
  import { page } from '$app/stores'
  import { onMount } from 'svelte'
  import { Button } from 'mono-svelte'
  import {
    buildSpecial1001FilmsEntryCommentsUrl,
    buildSpecial1001FilmsEntryRatingVoteUrl,
    buildSpecial1001FilmsEntryUrl,
    type BackendPostRating,
  } from '$lib/api/backend'
  import LoginModal from '$lib/components/auth/LoginModal.svelte'
  import PostBody from '$lib/components/lemmy/post/PostBody.svelte'
  import PostTemplateHeader from '$lib/components/site/post-templates/PostTemplateHeader.svelte'
  import PostComments from '$lib/components/site/PostComments.svelte'
  import { siteToken, siteUser } from '$lib/siteAuth'
  import type { SitePostTemplate } from '$lib/postTemplates'
  import { ArrowLeft, CheckCircle, Icon, LockClosed } from 'svelte-hero-icons'

  type FilmJourneyFilm = {
    title: string
    original_title?: string
    year?: number
    category?: string
    description?: string
    imdb_url?: string
    imdb_rating?: string
    poster_url?: string
    runtime_minutes?: number
    director?: string
    country?: string
    genres?: string
  }

  type FilmJourneyEntry = {
    position: number
    rating?: number | null
    comment?: string
    completed_at?: string | null
    film: FilmJourneyFilm
    discussion_post?: {
      id: number
      title: string
      content: string
      template?: SitePostTemplate | null
      post_ratings?: Record<string, BackendPostRating>
      comments_count?: number
    } | null
  }

  let entry: FilmJourneyEntry | null = null
  let loading = true
  let error = ''
  let authOpen = false

  const token = String($page.params.token || '')
  const commentsUrl = buildSpecial1001FilmsEntryCommentsUrl(token)
  const ratingVoteUrl = buildSpecial1001FilmsEntryRatingVoteUrl(token)
  const authHeaders = (): Record<string, string> =>
    $siteToken ? { Authorization: `Bearer ${$siteToken}` } : {}

  async function loadEntry() {
    if (!$siteToken || !$siteUser) {
      loading = false
      authOpen = true
      return
    }
    loading = true
    error = ''
    try {
      const response = await fetch(buildSpecial1001FilmsEntryUrl(token), {
        credentials: 'include',
        headers: authHeaders(),
      })
      const data = await response.json()
      if (!response.ok || !data?.ok) {
        throw new Error(data?.error || 'Не удалось открыть фильм')
      }
      entry = data.entry
    } catch (err) {
      error = (err as Error)?.message || 'Не удалось открыть фильм'
    }
    loading = false
  }

  $: film = entry?.film ?? null
  $: discussionPost = entry?.discussion_post ?? null

  onMount(loadEntry)
</script>

<svelte:head>
  <title>{film ? `${film.title} — 1001 фильм` : '1001 фильм'}</title>
  <meta name="robots" content="noindex,nofollow" />
</svelte:head>

<LoginModal bind:open={authOpen} initialMode="login" />

<section class="watch-page">
  <a class="back-link" href="/s/1001-films">
    <Icon src={ArrowLeft} size="16" mini />
    К проекту
  </a>

  {#if loading}
    <div class="state">Открываем секретную ссылку...</div>
  {:else if !$siteToken || !$siteUser}
    <div class="state">
      <Icon src={LockClosed} size="34" solid />
      <h1>Нужна авторизация</h1>
      <p>Эта страница доступна только участнику, которому пришла ссылка.</p>
      <Button color="primary" size="lg" on:click={() => (authOpen = true)}>Войти</Button>
    </div>
  {:else if error}
    <div class="state">
      <h1>{error}</h1>
      <p>Проверьте аккаунт или откройте последнюю ссылку из уведомлений.</p>
    </div>
  {:else if entry && film}
    <article class="film-card">
      <div class="film-heading">
        <span class="kicker">фильм #{entry.position}</span>
        <h1>{film.title}</h1>
        {#if entry.completed_at}
          <p class="done-note">
            <Icon src={CheckCircle} size="18" mini />
            Оценка и комментарий сохранены. Следующий фильм придёт по расписанию.
          </p>
        {:else}
          <p class="meta">
            Чтобы получить следующий фильм, поставьте оценку в блоке рейтинга и оставьте комментарий ниже.
          </p>
        {/if}
      </div>

      {#if discussionPost}
        {#if discussionPost.template}
          <div class="movie-template-header">
            <PostTemplateHeader
              template={discussionPost.template}
              fallbackTitle={discussionPost.title || film.title}
              postId={discussionPost.id}
            />
          </div>
        {/if}

        <PostBody
          body={discussionPost.content}
          template={discussionPost.template}
          postRatings={discussionPost.post_ratings ?? {}}
          postId={discussionPost.id}
          {ratingVoteUrl}
          title={discussionPost.title || film.title}
          showFullBody={true}
          class="film-post-body"
          on:rating={loadEntry}
        />

        <PostComments
          postId={discussionPost.id}
          {commentsUrl}
          on:comment={loadEntry}
        />
      {:else}
        <p class="meta">Не удалось подготовить обсуждение фильма.</p>
      {/if}
    </article>
  {/if}
</section>

<style>
  .watch-page {
    min-height: calc(100svh - 4.5rem);
    background: rgb(248 250 252);
    color: #0f172a;
    padding: clamp(1rem, 3vw, 2.25rem);
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: #475569;
    margin-bottom: 1.25rem;
  }

  .film-card,
  .state {
    max-width: 52rem;
    margin: 0 auto;
    border: 1px solid rgb(203 213 225);
    border-radius: 8px;
    background: rgb(255 255 255 / 0.84);
    box-shadow: 0 18px 48px rgb(15 23 42 / 0.08);
  }

  .film-card {
    padding: clamp(1.25rem, 3vw, 2.25rem);
  }

  .film-heading {
    margin-bottom: 1.25rem;
  }

  .movie-template-header {
    margin-bottom: 1.25rem;
  }

  .kicker {
    color: var(--btn-primary-background);
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0;
  }

  h1 {
    margin-top: 0.4rem;
    font-size: clamp(1.8rem, 4vw, 3rem);
    line-height: 1.05;
    letter-spacing: 0;
    font-weight: 500;
  }

  .meta,
  .done-note,
  .state p {
    color: #475569;
    line-height: 1.55;
  }

  .done-note {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    margin-top: 0.75rem;
  }

  .state {
    margin: 4rem auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  :global(.dark) .watch-page {
    background: rgb(9 9 11);
    color: #fafafa;
  }

  :global(.dark) .back-link,
  :global(.dark) .meta,
  :global(.dark) .done-note,
  :global(.dark) .state p {
    color: #a1a1aa;
  }

  :global(.dark) .film-card,
  :global(.dark) .state {
    border-color: rgb(39 39 42);
    background: rgb(9 9 11 / 0.8);
    box-shadow: 0 18px 48px rgb(0 0 0 / 0.24);
  }

  @media (max-width: 820px) {
    .watch-page {
      padding: 1rem;
    }
  }
</style>
