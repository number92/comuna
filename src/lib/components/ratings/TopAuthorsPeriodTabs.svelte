<script lang="ts">
  import type { BackendTopAuthorPeriod } from '$lib/api/backend'
  import {
    buildTopAuthorsPeriodHref,
    topAuthorPeriodOptions,
  } from '$lib/ratings/topAuthors'

  export let period: BackendTopAuthorPeriod
</script>

<div class="flex flex-wrap gap-2">
  {#each topAuthorPeriodOptions as option}
    <a
      href={buildTopAuthorsPeriodHref(option.value)}
      class:period-link--active={period === option.value}
      class="period-link"
    >
      {option.label}
    </a>
  {/each}
</div>

<style>
  .period-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 9999px;
    padding: 0.625rem 1rem;
    font-size: 0.9375rem;
    font-weight: 500;
    color: rgb(71 85 105);
    background: rgb(241 245 249);
    transition:
      background-color 0.15s ease,
      color 0.15s ease,
      transform 0.15s ease;
  }

  .period-link:hover {
    background: rgb(226 232 240);
    transform: translateY(-1px);
  }

  .period-link--active {
    color: white;
    background: rgb(15 23 42);
  }

  :global(.dark) .period-link {
    color: rgb(212 212 216);
    background: rgb(39 39 42);
  }

  :global(.dark) .period-link:hover {
    background: rgb(63 63 70);
  }

  :global(.dark) .period-link--active {
    color: rgb(24 24 27);
    background: rgb(244 244 245);
  }
</style>
