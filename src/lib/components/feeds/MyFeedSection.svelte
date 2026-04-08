<script lang="ts">
  import { browser } from '$app/environment'
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import {
    buildTagsListUrl,
    buildThematicFeedsListUrl,
    type BackendPost,
    type BackendThematicFeed,
  } from '$lib/api/backend'
  import FeedPostsList from '$lib/components/feeds/FeedPostsList.svelte'
  import {
    buildMyFeedSettingsFromFolderPreset,
    hasMyFeedCustomizations,
  } from '$lib/feeds/myFeed'
  import { siteUser } from '$lib/siteAuth'
  import { userSettings } from '$lib/settings'
  import { normalizeTag } from '$lib/tags'
  import { Button } from 'mono-svelte'

  export let posts: BackendPost[] = []
  export let loadingMore = false

  const moodDurationMs = 3 * 60 * 60 * 1000
  const moodOptions: Array<{ label: string; value: 'funny' | 'serious' | 'sad' }> = [
    { label: 'Веселое', value: 'funny' },
    { label: 'Серьезное', value: 'serious' },
    { label: 'Грустное', value: 'sad' },
  ]

  let myFeedSettingsOpen = false
  let myFeedSuggestedFolders: BackendThematicFeed[] = []
  let myFeedSuggestedFoldersLoading = false
  let myFeedSuggestedFoldersLoaded = false
  let myFeedSuggestedFoldersError = ''
  let tagMoodMap = new Map<string, string>()
  let tagLemmaMap = new Map<string, string>()
  let tagMoodLoading = false
  let moodExpiryTimer: ReturnType<typeof setTimeout> | null = null
  let moodTagSet = new Set<string>()
  let filteredPosts: BackendPost[] = []

  const openMyFeedSettings = () => {
    myFeedSettingsOpen = true
  }

  const toggleMyFeedSettings = () => {
    myFeedSettingsOpen = !myFeedSettingsOpen
  }

  const loadMyFeedSuggestedFolders = async () => {
    if (!browser || myFeedSuggestedFoldersLoading) return
    myFeedSuggestedFoldersLoading = true
    myFeedSuggestedFoldersError = ''
    try {
      const response = await fetch(buildThematicFeedsListUrl())
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload?.error || 'Не удалось загрузить список папок')
      }
      myFeedSuggestedFolders = payload.folders ?? payload.feeds ?? []
      myFeedSuggestedFoldersLoaded = true
    } catch (error) {
      myFeedSuggestedFoldersError =
        error instanceof Error ? error.message : 'Ошибка загрузки папок'
      myFeedSuggestedFoldersLoaded = true
    } finally {
      myFeedSuggestedFoldersLoading = false
    }
  }

  const loadTagMoods = async () => {
    if (!browser || tagMoodLoading || tagMoodMap.size) return
    tagMoodLoading = true
    try {
      const response = await fetch(buildTagsListUrl())
      if (response.ok) {
        const payload = await response.json()
        const entries =
          payload.tags?.map((tag: { name: string; lemma?: string; mood: string }) => [
            normalizeTag(tag.lemma ?? tag.name),
            tag.mood,
          ]) ?? []
        const lemmaEntries =
          payload.tags?.map((tag: { name: string; lemma?: string }) => [
            normalizeTag(tag.name),
            normalizeTag(tag.lemma ?? tag.name),
          ]) ?? []
        tagMoodMap = new Map(entries)
        tagLemmaMap = new Map(lemmaEntries)
      }
    } catch (error) {
      console.error('Failed to load tag moods:', error)
    } finally {
      tagMoodLoading = false
    }
  }

  const selectMood = (value: 'funny' | 'serious' | 'sad') => {
    if (moodActive && myFeedMood === value) {
      clearMood()
      return
    }
    const expiresAt = Date.now() + moodDurationMs
    $userSettings = {
      ...$userSettings,
      myFeedMood: value,
      myFeedMoodExpiresAt: expiresAt,
    }
  }

  const clearMood = () => {
    $userSettings = {
      ...$userSettings,
      myFeedMood: null,
      myFeedMoodExpiresAt: null,
    }
  }

  const scheduleMoodClear = (expiresAt: number | null) => {
    if (!browser) return
    if (moodExpiryTimer) {
      window.clearTimeout(moodExpiryTimer)
      moodExpiryTimer = null
    }
    if (!expiresAt) return
    const delay = expiresAt - Date.now()
    if (delay <= 0) {
      userSettings.update((settings) => ({
        ...settings,
        myFeedMood: null,
        myFeedMoodExpiresAt: null,
      }))
      return
    }
    moodExpiryTimer = window.setTimeout(() => {
      userSettings.update((settings) => ({
        ...settings,
        myFeedMood: null,
        myFeedMoodExpiresAt: null,
      }))
    }, delay)
  }

  const applyFolderPresetToMyFeed = async (folderPreset: BackendThematicFeed | null) => {
    if (!folderPreset) return
    if (!$siteUser) {
      const next = encodeURIComponent(`${$page.url.pathname}${$page.url.search}`)
      goto(`/account?next=${next}`)
      return
    }
    if (browser && hasMyFeedCustomizations($userSettings)) {
      const confirmed = window.confirm(
        'У вас уже настроена "Моя лента". Нажатие на кнопку заменит текущие настройки настройками папки. После этого вы сможете дополнительно настроить свою ленту. Продолжить?'
      )
      if (!confirmed) return
    }
    $userSettings = buildMyFeedSettingsFromFolderPreset($userSettings, folderPreset)
    goto('/?feed=mine')
  }

  const authorKey = (backendPost: { author?: { username?: string } }) =>
    (backendPost.author?.username ?? '').trim().toLowerCase()

  const hiddenAuthorKeys = new Set(
    ($userSettings.hiddenAuthors ?? []).map((value) => value.toLowerCase())
  )

  const isAuthorVisible = (backendPost: { author?: { username?: string } }) => {
    const key = authorKey(backendPost)
    if (!key) return true
    return !hiddenAuthorKeys.has(key)
  }

  $: selectedRubrics = $userSettings.myFeedRubrics ?? []
  $: selectedAuthors = $userSettings.myFeedAuthors ?? []
  $: selectedMyFeedTags = $userSettings.myFeedTags ?? []
  $: selectedMyFeedComuns = $userSettings.myFeedComuns ?? []
  $: myFeedHasBaseSettings =
    selectedRubrics.length > 0 ||
    selectedAuthors.length > 0 ||
    selectedMyFeedTags.length > 0 ||
    selectedMyFeedComuns.length > 0
  $: myFeedMood = $userSettings.myFeedMood ?? null
  $: myFeedMoodExpiresAt = $userSettings.myFeedMoodExpiresAt ?? null
  $: moodActive =
    !!myFeedMood &&
    !!myFeedMoodExpiresAt &&
    Date.now() < myFeedMoodExpiresAt
  $: effectiveMood = moodActive ? myFeedMood : null
  $: moodTagSet =
    effectiveMood && tagMoodMap.size
      ? new Set(
          Array.from(tagMoodMap.entries())
            .filter(([, mood]) => mood === effectiveMood)
            .map(([name]) => name)
        )
      : new Set<string>()
  $: filteredPosts =
    effectiveMood && tagMoodMap.size
      ? posts
          .filter((post) =>
            (post.tags ?? []).some((tag) => {
              const rawName = typeof tag === 'string' ? tag : tag.name
              const normalized = normalizeTag(rawName)
              const lemma =
                typeof tag === 'string'
                  ? tagLemmaMap.get(normalized) ?? normalized
                  : normalizeTag(tag.lemma ?? tag.name)
              return moodTagSet.has(lemma)
            })
          )
          .filter(isAuthorVisible)
      : effectiveMood
        ? []
        : posts.filter(isAuthorVisible)

  $: if (effectiveMood) {
    void loadTagMoods()
  }

  $: if (browser && !!$siteUser && !myFeedHasBaseSettings && !myFeedSuggestedFoldersLoaded) {
    void loadMyFeedSuggestedFolders()
  }

  $: if (!$siteUser) {
    myFeedSuggestedFolders = []
    myFeedSuggestedFoldersLoaded = false
    myFeedSuggestedFoldersLoading = false
    myFeedSuggestedFoldersError = ''
  }

  $: scheduleMoodClear(myFeedMoodExpiresAt)
</script>

<div class="flex flex-col gap-4">
  <div class="flex items-center justify-between gap-3">
    <h1 class="text-2xl font-semibold text-slate-900 dark:text-zinc-100">
      Моя лента
    </h1>
    {#if $siteUser}
      <button
        type="button"
        class="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 dark:text-zinc-400 dark:hover:text-zinc-200"
        on:click={toggleMyFeedSettings}
        aria-expanded={myFeedSettingsOpen}
      >
        Настроить
      </button>
    {/if}
  </div>

  {#if !$siteUser}
    <div class="text-base text-slate-500">
      После регистрации вы получите доступ к персонализируемой ленте, которую сможете настроить и видеть только интересные вам посты.
    </div>
  {:else}
    {#if myFeedSettingsOpen}
      <div class="rounded-2xl border border-slate-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div class="flex flex-col gap-4">
          <div class="flex flex-wrap gap-2">
            {#each moodOptions as mood}
              <Button
                color={effectiveMood === mood.value ? 'primary' : 'ghost'}
                on:click={() => selectMood(mood.value)}
              >
                {mood.label}
              </Button>
            {/each}
          </div>
          <div class="text-xs text-slate-500 dark:text-zinc-400">
            Можно быстро настроить ленту под настроение на 3 часа.
          </div>
          <div class="text-sm text-slate-600 dark:text-zinc-300">
            Выбор сообществ и составление черного списка доступны в настройках сайта.
          </div>
          <a href="/settings" class="text-sm text-blue-600 hover:underline dark:text-blue-400">
            Перейти в настройки
          </a>
        </div>
      </div>
    {:else if !myFeedHasBaseSettings}
      <div class="rounded-2xl border border-slate-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <div class="text-sm text-slate-700 dark:text-zinc-200">
              Ваша лента пока не настроена.
            </div>
            <div class="text-sm text-slate-500 dark:text-zinc-400">
              Вы можете настроить ее вручную или выбрать готовую папку, которая станет вашей лентой.
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <Button color="ghost" on:click={openMyFeedSettings}>
              Настроить мою ленту
            </Button>
            <a href="/settings" class="inline-flex items-center text-sm text-blue-600 hover:underline dark:text-blue-400">
              Открыть настройки сайта
            </a>
          </div>
          <div class="flex flex-col gap-3">
            <div class="text-sm font-medium text-slate-800 dark:text-zinc-200">
              Или выберите готовую папку
            </div>
            {#if myFeedSuggestedFoldersLoading}
              <div class="text-sm text-slate-500 dark:text-zinc-400">Загружаем папки...</div>
            {:else if myFeedSuggestedFoldersError}
              <div class="text-sm text-rose-600 dark:text-rose-300">{myFeedSuggestedFoldersError}</div>
            {:else if myFeedSuggestedFolders.length}
              <div class="grid gap-2 md:grid-cols-2">
                {#each myFeedSuggestedFolders as folder}
                  <div class="rounded-xl border border-slate-200 p-3 dark:border-zinc-800">
                    <div class="flex flex-col gap-2 min-w-0">
                      <div class="min-w-0">
                        <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                          {folder.name}
                        </div>
                        {#if folder.description}
                          <div class="line-clamp-2 text-xs text-slate-500 dark:text-zinc-400">
                            {folder.description}
                          </div>
                        {/if}
                      </div>
                      <div class="text-xs text-slate-500 dark:text-zinc-400">
                        {folder.authors_count ?? 0} авторов · {folder.tags_count ?? 0} тегов · {folder.blocked_tags_count ?? 0} искл. тегов
                      </div>
                      <div class="flex flex-wrap gap-2">
                        <Button on:click={() => applyFolderPresetToMyFeed(folder)}>
                          Сделать моей лентой
                        </Button>
                        <a
                          href={`/?feed=thematic&theme=${encodeURIComponent(folder.slug)}`}
                          class="inline-flex items-center text-sm text-blue-600 hover:underline dark:text-blue-400"
                        >
                          Открыть папку
                        </a>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="text-sm text-slate-500 dark:text-zinc-400">
                Пока нет готовых папок. Можно настроить ленту вручную.
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}

    {#if effectiveMood && tagMoodLoading}
      <div class="text-sm text-slate-500">Загружаем теги настроения...</div>
    {/if}

    {#if filteredPosts.length}
      <FeedPostsList posts={filteredPosts} {loadingMore} />
    {:else if !myFeedHasBaseSettings}
      <div class="text-base text-slate-500">Выберите настройки или папку, чтобы запустить “Мою ленту”.</div>
    {:else}
      <div class="text-base text-slate-500">Пока нет публикаций.</div>
    {/if}
  {/if}
</div>
