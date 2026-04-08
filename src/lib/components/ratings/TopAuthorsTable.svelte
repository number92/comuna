<script lang="ts">
  import Avatar from '$lib/components/ui/Avatar.svelte'
  import type { BackendTopAuthor, BackendTopAuthorPeriod } from '$lib/api/backend'
  import {
    formatTopAuthorNumber,
    topAuthorRatingLabelMap,
  } from '$lib/ratings/topAuthors'

  export let authors: BackendTopAuthor[] = []
  export let period: BackendTopAuthorPeriod = 'month'
  export let totalAuthors = 0
</script>

<section class="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
  <div class="flex items-center justify-between gap-4 border-b border-slate-200 px-5 py-4 dark:border-zinc-800 sm:px-6">
    <div>
      <div class="text-lg font-semibold text-slate-950 dark:text-zinc-50">
        Весь рейтинг
      </div>
      <div class="text-sm text-slate-500 dark:text-zinc-400">
        Всего авторов: {formatTopAuthorNumber(totalAuthors || authors.length)}
      </div>
    </div>
    <div class="hidden text-sm text-slate-500 dark:text-zinc-400 sm:block">
      {topAuthorRatingLabelMap[period]}
    </div>
  </div>

  <div class="flex flex-col">
    {#each authors as author, offset}
      {@const rank = offset + 4}
      <a href={`/${author.username}`} class="rating-row">
        <div class="flex min-w-0 flex-1 items-center gap-4">
          <div class="row-rank">
            {rank}
          </div>
          <Avatar
            url={author.avatar_url || undefined}
            alt={author.title || author.username}
            width={44}
            class_="h-11 w-11 rounded-full"
          />
          <div class="min-w-0 flex-1">
            <div class="truncate text-base font-semibold text-slate-900 dark:text-zinc-100">
              {author.title || author.username}
            </div>
            <div class="truncate text-sm text-slate-500 dark:text-zinc-400">
              @{author.username}
            </div>
          </div>
        </div>

        <div class="flex shrink-0 items-center gap-6 text-right">
          <div class="min-w-[88px]">
            <div class="text-xs uppercase tracking-wide text-slate-400 dark:text-zinc-500">
              Рейтинг
            </div>
            <div class="text-base font-semibold text-slate-900 dark:text-zinc-100">
              {formatTopAuthorNumber(author.rating ?? author.score)}
            </div>
          </div>
          <div class="min-w-[72px]">
            <div class="text-xs uppercase tracking-wide text-slate-400 dark:text-zinc-500">
              Посты
            </div>
            <div class="text-base font-semibold text-slate-900 dark:text-zinc-100">
              {formatTopAuthorNumber(author.posts_count)}
            </div>
          </div>
        </div>
      </a>
    {/each}
  </div>
</section>

<style>
  .rating-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-top: 1px solid rgb(241 245 249);
    transition: background-color 0.15s ease;
  }

  .rating-row:hover {
    background: rgb(248 250 252);
  }

  :global(.dark) .rating-row {
    border-top-color: rgb(39 39 42);
  }

  :global(.dark) .rating-row:hover {
    background: rgb(39 39 42 / 0.65);
  }

  .row-rank {
    width: 2.25rem;
    text-align: center;
    font-size: 1rem;
    font-weight: 700;
    color: rgb(100 116 139);
    flex-shrink: 0;
  }

  @media (max-width: 640px) {
    .rating-row {
      flex-direction: column;
      align-items: flex-start;
    }

    .rating-row > :last-child {
      width: 100%;
      justify-content: space-between;
    }
  }
</style>
