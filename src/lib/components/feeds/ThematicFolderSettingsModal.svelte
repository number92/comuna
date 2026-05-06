<script lang="ts">
  import { browser } from '$app/environment'
  import type { BackendThematicFeed } from '$lib/api/backend'
  import { buildThematicFeedsManageUrl } from '$lib/api/backend'
  import { siteToken } from '$lib/siteAuth'
  import { Button, Modal } from 'mono-svelte'

  type FolderManageAuthorOption = {
    id: number
    username: string
    title?: string | null
    description?: string | null
  }

  type FolderManageTagOption = {
    id: number
    name: string
    lemma?: string | null
  }

  type FolderAuthorSelectionKey = 'author_ids' | 'excluded_author_ids'
  type FolderTagSelectionKey = 'tag_ids' | 'excluded_tag_ids'
  type FolderSettingsSelectionKey = FolderAuthorSelectionKey | FolderTagSelectionKey

  export let open = false
  export let thematicFeedSlug = ''
  export let onClose: () => void = () => {}
  export let onUpdatedFolder: (folder: BackendThematicFeed) => void = () => {}
  export let onRefreshFeed: () => Promise<void> | void = () => {}

  let folderSettingsLoading = false
  let folderSettingsSaving = false
  let folderSettingsSaveQueued = false
  let folderSettingsShouldRefreshFeed = false
  let folderSettingsError = ''
  let folderSettingsSuccess = ''
  let folderSettingsDraft: BackendThematicFeed | null = null
  let folderSettingsAuthorOptions: FolderManageAuthorOption[] = []
  let folderSettingsTagOptions: FolderManageTagOption[] = []
  let filteredFolderAuthorOptions: FolderManageAuthorOption[] = []
  let filteredFolderExcludedAuthorOptions: FolderManageAuthorOption[] = []
  let filteredFolderTagOptions: FolderManageTagOption[] = []
  let filteredFolderExcludedTagOptions: FolderManageTagOption[] = []
  let folderSettingsAuthorSearch = ''
  let folderSettingsExcludedAuthorSearch = ''
  let folderSettingsTagSearch = ''
  let folderSettingsExcludedTagSearch = ''
  let lastLoadedFolderKey = ''

  const cloneFolderSettingsDraft = (folder: BackendThematicFeed | null): BackendThematicFeed | null =>
    folder ? JSON.parse(JSON.stringify(folder)) : null

  const normalizeFolderSearch = (value: string) => value.trim().toLowerCase()

  const matchesFolderAuthorSearch = (author: FolderManageAuthorOption, query: string) => {
    if (!query) return true
    const haystack = [
      author.username,
      author.title ?? '',
      author.description ?? '',
    ]
      .join(' ')
      .toLowerCase()
    return haystack.includes(query)
  }

  const matchesFolderTagSearch = (tag: FolderManageTagOption, query: string) => {
    if (!query) return true
    return [tag.name, tag.lemma ?? '']
      .join(' ')
      .toLowerCase()
      .includes(query)
  }

  const getFolderSelectedIds = (key: FolderSettingsSelectionKey): number[] => {
    if (!folderSettingsDraft) return []
    const values = (folderSettingsDraft as any)[key]
    return Array.isArray(values)
      ? values.filter((value) => Number.isFinite(value) && value > 0)
      : []
  }

  const getFolderAuthorOptionById = (id: number): FolderManageAuthorOption | null =>
    folderSettingsAuthorOptions.find((author) => author.id === id) ?? null

  const getFolderSelectedAuthorIds = (key: FolderAuthorSelectionKey): number[] =>
    getFolderSelectedIds(key)

  const getFolderSelectedAuthors = (key: FolderAuthorSelectionKey): FolderManageAuthorOption[] =>
    getFolderSelectedAuthorIds(key)
      .map((id) => getFolderAuthorOptionById(id))
      .filter(Boolean) as FolderManageAuthorOption[]

  const isFolderAuthorSelected = (key: FolderAuthorSelectionKey, authorId: number) =>
    getFolderSelectedAuthorIds(key).includes(authorId)

  const getFolderAvailableAuthors = (
    key: FolderAuthorSelectionKey,
    candidates: FolderManageAuthorOption[]
  ) => candidates.filter((author) => !isFolderAuthorSelected(key, author.id))

  const getFolderTagOptionById = (id: number): FolderManageTagOption | null =>
    folderSettingsTagOptions.find((tag) => tag.id === id) ?? null

  const getFolderSelectedTags = (key: FolderTagSelectionKey): FolderManageTagOption[] =>
    getFolderSelectedIds(key)
      .map((id) => getFolderTagOptionById(id))
      .filter(Boolean) as FolderManageTagOption[]

  const isFolderTagSelected = (key: FolderTagSelectionKey, tagId: number) =>
    getFolderSelectedIds(key).includes(tagId)

  const getFolderAvailableTags = (
    key: FolderTagSelectionKey,
    candidates: FolderManageTagOption[]
  ) => candidates.filter((tag) => !isFolderTagSelected(key, tag.id))

  const touchFolderSettingsDraft = () => {
    if (!folderSettingsDraft) return
    folderSettingsDraft = { ...folderSettingsDraft }
  }

  const addFolderAuthorToSelection = (key: FolderAuthorSelectionKey, authorId: number) => {
    if (!folderSettingsDraft || !Number.isFinite(authorId) || authorId <= 0) return
    const next = new Set(getFolderSelectedAuthorIds(key))
    next.add(authorId)
    ;(folderSettingsDraft as any)[key] = Array.from(next)
    touchFolderSettingsDraft()
    queueCurrentFolderSettingsSave()
  }

  const removeFolderAuthorFromSelection = (key: FolderAuthorSelectionKey, authorId: number) => {
    if (!folderSettingsDraft) return
    ;(folderSettingsDraft as any)[key] = getFolderSelectedAuthorIds(key).filter((id) => id !== authorId)
    touchFolderSettingsDraft()
    queueCurrentFolderSettingsSave()
  }

  const addFolderTagToSelection = (key: FolderTagSelectionKey, tagId: number) => {
    if (!folderSettingsDraft || !Number.isFinite(tagId) || tagId <= 0) return
    const next = new Set(getFolderSelectedIds(key))
    next.add(tagId)
    ;(folderSettingsDraft as any)[key] = Array.from(next)
    touchFolderSettingsDraft()
    queueCurrentFolderSettingsSave()
  }

  const removeFolderTagFromSelection = (key: FolderTagSelectionKey, tagId: number) => {
    if (!folderSettingsDraft) return
    ;(folderSettingsDraft as any)[key] = getFolderSelectedIds(key).filter((id) => id !== tagId)
    touchFolderSettingsDraft()
    queueCurrentFolderSettingsSave()
  }

  const loadCurrentFolderSettings = async () => {
    if (!browser || !$siteToken || !thematicFeedSlug) return
    folderSettingsLoading = true
    folderSettingsError = ''
    folderSettingsSuccess = ''
    try {
      const response = await fetch(buildThematicFeedsManageUrl(), {
        headers: {
          Authorization: `Bearer ${$siteToken}`,
        },
      })
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload?.error || 'Не удалось загрузить настройки папки')
      }
      folderSettingsAuthorOptions = payload.options?.authors ?? []
      folderSettingsTagOptions = payload.options?.tags ?? []
      folderSettingsSaveQueued = false
      folderSettingsShouldRefreshFeed = false
      folderSettingsAuthorSearch = ''
      folderSettingsExcludedAuthorSearch = ''
      folderSettingsTagSearch = ''
      folderSettingsExcludedTagSearch = ''
      const currentFolder =
        (payload.folders ?? []).find(
          (folder: BackendThematicFeed) => folder.slug === thematicFeedSlug
        ) ?? null
      if (!currentFolder) {
        throw new Error('Папка недоступна для редактирования')
      }
      folderSettingsDraft = cloneFolderSettingsDraft(currentFolder)
      lastLoadedFolderKey = thematicFeedSlug
    } catch (error) {
      folderSettingsError =
        error instanceof Error ? error.message : 'Ошибка загрузки настроек папки'
    } finally {
      folderSettingsLoading = false
    }
  }

  const refreshCurrentFolderFeedAfterSettingsSave = async () => {
    await onRefreshFeed()
  }

  const flushCurrentFolderSettingsSaveQueue = async () => {
    if (folderSettingsSaving || !folderSettingsSaveQueued) return
    if (!folderSettingsDraft || !thematicFeedSlug || !$siteToken) return
    folderSettingsSaving = true
    folderSettingsError = ''
    let refreshFeedAfterSave = false
    try {
      while (folderSettingsSaveQueued) {
        folderSettingsSaveQueued = false
        refreshFeedAfterSave = refreshFeedAfterSave || folderSettingsShouldRefreshFeed
        folderSettingsShouldRefreshFeed = false
        const draft = folderSettingsDraft
        if (!draft) break
        const response = await fetch(buildThematicFeedsManageUrl(thematicFeedSlug), {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${$siteToken}`,
          },
          body: JSON.stringify({
            author_ids: draft.author_ids ?? [],
            excluded_author_ids: draft.excluded_author_ids ?? [],
            tag_ids: draft.tag_ids ?? [],
            excluded_tag_ids: draft.excluded_tag_ids ?? [],
          }),
        })
        const payload = await response.json().catch(() => ({}))
        if (!response.ok) {
          throw new Error(payload?.error || 'Не удалось сохранить настройки папки')
        }
        const updatedFolder = (payload.folder ?? null) as BackendThematicFeed | null
        if (updatedFolder) {
          onUpdatedFolder(updatedFolder)
        }
        folderSettingsSuccess = 'Изменения сохранены'
      }
      if (refreshFeedAfterSave) {
        await refreshCurrentFolderFeedAfterSettingsSave()
      }
    } catch (error) {
      folderSettingsError =
        error instanceof Error ? error.message : 'Ошибка сохранения настроек папки'
    } finally {
      folderSettingsSaving = false
      if (folderSettingsSaveQueued) {
        void flushCurrentFolderSettingsSaveQueue()
      }
    }
  }

  const queueCurrentFolderSettingsSave = (refreshFeed = true) => {
    folderSettingsSaveQueued = true
    if (refreshFeed) {
      folderSettingsShouldRefreshFeed = true
    }
    void flushCurrentFolderSettingsSaveQueue()
  }

  const handleClose = () => {
    folderSettingsSaveQueued = false
    folderSettingsShouldRefreshFeed = false
    folderSettingsError = ''
    folderSettingsSuccess = ''
    onClose()
  }

  $: filteredFolderAuthorOptions = folderSettingsAuthorOptions.filter((author) =>
    matchesFolderAuthorSearch(author, normalizeFolderSearch(folderSettingsAuthorSearch))
  )
  $: filteredFolderExcludedAuthorOptions = folderSettingsAuthorOptions.filter((author) =>
    matchesFolderAuthorSearch(author, normalizeFolderSearch(folderSettingsExcludedAuthorSearch))
  )
  $: filteredFolderTagOptions = folderSettingsTagOptions.filter((tag) =>
    matchesFolderTagSearch(tag, normalizeFolderSearch(folderSettingsTagSearch))
  )
  $: filteredFolderExcludedTagOptions = folderSettingsTagOptions.filter((tag) =>
    matchesFolderTagSearch(tag, normalizeFolderSearch(folderSettingsExcludedTagSearch))
  )

  $: if (open && thematicFeedSlug && thematicFeedSlug !== lastLoadedFolderKey) {
    void loadCurrentFolderSettings()
  }

  $: if (!open) {
    lastLoadedFolderKey = ''
  }
</script>

<Modal bind:open={open} on:close={handleClose}>
  <div class="w-full max-w-[48rem] flex flex-col gap-4">
    <div>
      <h2 class="text-xl font-semibold text-slate-900 dark:text-zinc-100">
        Настройки папки
      </h2>
      <p class="mt-1 text-sm text-slate-500 dark:text-zinc-400">
        Добавляйте и исключайте авторов, сообщества и теги для текущей папки. Изменения сохраняются автоматически.
      </p>
    </div>

    {#if folderSettingsError}
      <div class="rounded-xl border border-rose-200 bg-rose-50/70 p-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950/20 dark:text-rose-300">
        {folderSettingsError}
      </div>
    {/if}
    {#if folderSettingsSuccess}
      <div class="rounded-xl border border-emerald-200 bg-emerald-50/70 p-3 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/20 dark:text-emerald-300">
        {folderSettingsSuccess}
      </div>
    {/if}
    {#if folderSettingsSaving}
      <div class="text-xs text-slate-500 dark:text-zinc-400">
        Сохраняем изменения...
      </div>
    {/if}

    {#if folderSettingsLoading}
      <div class="text-sm text-slate-500 dark:text-zinc-400">Загружаем настройки папки...</div>
    {:else if folderSettingsDraft}
      <div class="flex flex-col gap-4">
        <label class="flex flex-col gap-1 text-sm min-w-0">
          <span>Авторы</span>
          <input
            type="text"
            bind:value={folderSettingsAuthorSearch}
            placeholder="Поиск по нику, названию канала, описанию"
            class="rounded-lg border border-slate-200 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950"
          />
          <div class="max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white dark:border-zinc-700 dark:bg-zinc-950">
            {#each getFolderAvailableAuthors('author_ids', filteredFolderAuthorOptions).slice(0, 30) as author}
              <div class="flex items-start justify-between gap-3 border-b border-slate-100 px-3 py-2 last:border-b-0 dark:border-zinc-800">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    @{author.username}
                  </div>
                  {#if author.title}
                    <div class="line-clamp-2 text-xs text-slate-700 dark:text-zinc-300">
                      {author.title}
                    </div>
                  {/if}
                  {#if author.description}
                    <div class="line-clamp-2 text-xs text-slate-500 dark:text-zinc-400">
                      {author.description}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs font-medium hover:bg-slate-50 dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => addFolderAuthorToSelection('author_ids', author.id)}
                >
                  Добавить
                </button>
              </div>
            {:else}
              <div class="px-3 py-3 text-xs text-slate-500 dark:text-zinc-400">
                Ничего не найдено
              </div>
            {/each}
          </div>
          <div class="mt-2 flex flex-col gap-2">
            <div class="text-xs uppercase tracking-wide text-slate-500 dark:text-zinc-400">
              Добавленные авторы
            </div>
            {#each getFolderSelectedAuthors('author_ids') as author}
              <div class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50/70 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900/60">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    @{author.username}
                  </div>
                  {#if author.title}
                    <div class="line-clamp-2 text-xs text-slate-700 dark:text-zinc-300">
                      {author.title}
                    </div>
                  {/if}
                  {#if author.description}
                    <div class="line-clamp-2 text-xs text-slate-500 dark:text-zinc-400">
                      {author.description}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs hover:bg-white dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => removeFolderAuthorFromSelection('author_ids', author.id)}
                >
                  Убрать
                </button>
              </div>
            {:else}
              <div class="text-xs text-slate-500 dark:text-zinc-400">
                Пока никто не добавлен
              </div>
            {/each}
          </div>
        </label>

        <label class="flex flex-col gap-1 text-sm min-w-0">
          <span>Исключенные авторы</span>
          <input
            type="text"
            bind:value={folderSettingsExcludedAuthorSearch}
            placeholder="Поиск по нику, названию канала, описанию"
            class="rounded-lg border border-slate-200 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950"
          />
          <div class="max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white dark:border-zinc-700 dark:bg-zinc-950">
            {#each getFolderAvailableAuthors('excluded_author_ids', filteredFolderExcludedAuthorOptions).slice(0, 30) as author}
              <div class="flex items-start justify-between gap-3 border-b border-slate-100 px-3 py-2 last:border-b-0 dark:border-zinc-800">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    @{author.username}
                  </div>
                  {#if author.title}
                    <div class="line-clamp-2 text-xs text-slate-700 dark:text-zinc-300">
                      {author.title}
                    </div>
                  {/if}
                  {#if author.description}
                    <div class="line-clamp-2 text-xs text-slate-500 dark:text-zinc-400">
                      {author.description}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs font-medium hover:bg-slate-50 dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => addFolderAuthorToSelection('excluded_author_ids', author.id)}
                >
                  Добавить
                </button>
              </div>
            {:else}
              <div class="px-3 py-3 text-xs text-slate-500 dark:text-zinc-400">
                Ничего не найдено
              </div>
            {/each}
          </div>
          <div class="mt-2 flex flex-col gap-2">
            <div class="text-xs uppercase tracking-wide text-slate-500 dark:text-zinc-400">
              Исключенные авторы
            </div>
            {#each getFolderSelectedAuthors('excluded_author_ids') as author}
              <div class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50/70 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900/60">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    @{author.username}
                  </div>
                  {#if author.title}
                    <div class="line-clamp-2 text-xs text-slate-700 dark:text-zinc-300">
                      {author.title}
                    </div>
                  {/if}
                  {#if author.description}
                    <div class="line-clamp-2 text-xs text-slate-500 dark:text-zinc-400">
                      {author.description}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs hover:bg-white dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => removeFolderAuthorFromSelection('excluded_author_ids', author.id)}
                >
                  Убрать
                </button>
              </div>
            {:else}
              <div class="text-xs text-slate-500 dark:text-zinc-400">
                Пока никого нет в исключениях
              </div>
            {/each}
          </div>
        </label>

        <label class="flex flex-col gap-1 text-sm min-w-0">
          <span>Теги</span>
          <input
            type="text"
            bind:value={folderSettingsTagSearch}
            placeholder="Поиск по тегу или лемме"
            class="rounded-lg border border-slate-200 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950"
          />
          <div class="max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white dark:border-zinc-700 dark:bg-zinc-950">
            {#each getFolderAvailableTags('tag_ids', filteredFolderTagOptions).slice(0, 40) as tag}
              <div class="flex items-start justify-between gap-3 border-b border-slate-100 px-3 py-2 last:border-b-0 dark:border-zinc-800">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    {tag.name}
                  </div>
                  {#if tag.lemma && tag.lemma.toLowerCase() !== tag.name.toLowerCase()}
                    <div class="text-xs text-slate-500 dark:text-zinc-400">
                      Лемма: {tag.lemma}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs font-medium hover:bg-slate-50 dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => addFolderTagToSelection('tag_ids', tag.id)}
                >
                  Добавить
                </button>
              </div>
            {:else}
              <div class="px-3 py-3 text-xs text-slate-500 dark:text-zinc-400">
                Ничего не найдено
              </div>
            {/each}
          </div>
          <div class="mt-2 flex flex-col gap-2">
            <div class="text-xs uppercase tracking-wide text-slate-500 dark:text-zinc-400">
              Выбранные теги
            </div>
            {#each getFolderSelectedTags('tag_ids') as tag}
              <div class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50/70 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900/60">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    {tag.name}
                  </div>
                  {#if tag.lemma && tag.lemma.toLowerCase() !== tag.name.toLowerCase()}
                    <div class="text-xs text-slate-500 dark:text-zinc-400">
                      Лемма: {tag.lemma}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs hover:bg-white dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => removeFolderTagFromSelection('tag_ids', tag.id)}
                >
                  Убрать
                </button>
              </div>
            {:else}
              <div class="text-xs text-slate-500 dark:text-zinc-400">
                Пока теги не выбраны
              </div>
            {/each}
          </div>
        </label>

        <label class="flex flex-col gap-1 text-sm min-w-0">
          <span>Исключенные теги</span>
          <input
            type="text"
            bind:value={folderSettingsExcludedTagSearch}
            placeholder="Поиск по тегу или лемме"
            class="rounded-lg border border-slate-200 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-950"
          />
          <div class="max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white dark:border-zinc-700 dark:bg-zinc-950">
            {#each getFolderAvailableTags('excluded_tag_ids', filteredFolderExcludedTagOptions).slice(0, 40) as tag}
              <div class="flex items-start justify-between gap-3 border-b border-slate-100 px-3 py-2 last:border-b-0 dark:border-zinc-800">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    {tag.name}
                  </div>
                  {#if tag.lemma && tag.lemma.toLowerCase() !== tag.name.toLowerCase()}
                    <div class="text-xs text-slate-500 dark:text-zinc-400">
                      Лемма: {tag.lemma}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs font-medium hover:bg-slate-50 dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => addFolderTagToSelection('excluded_tag_ids', tag.id)}
                >
                  Добавить
                </button>
              </div>
            {:else}
              <div class="px-3 py-3 text-xs text-slate-500 dark:text-zinc-400">
                Ничего не найдено
              </div>
            {/each}
          </div>
          <div class="mt-2 flex flex-col gap-2">
            <div class="text-xs uppercase tracking-wide text-slate-500 dark:text-zinc-400">
              Исключенные теги
            </div>
            {#each getFolderSelectedTags('excluded_tag_ids') as tag}
              <div class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50/70 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900/60">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-slate-900 dark:text-zinc-100">
                    {tag.name}
                  </div>
                  {#if tag.lemma && tag.lemma.toLowerCase() !== tag.name.toLowerCase()}
                    <div class="text-xs text-slate-500 dark:text-zinc-400">
                      Лемма: {tag.lemma}
                    </div>
                  {/if}
                </div>
                <button
                  type="button"
                  class="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs hover:bg-white dark:border-zinc-700 dark:hover:bg-zinc-800"
                  on:click={() => removeFolderTagFromSelection('excluded_tag_ids', tag.id)}
                >
                  Убрать
                </button>
              </div>
            {:else}
              <div class="text-xs text-slate-500 dark:text-zinc-400">
                Пока нет исключенных тегов
              </div>
            {/each}
          </div>
        </label>
      </div>
    {:else}
      <div class="text-sm text-slate-500 dark:text-zinc-400">
        Не удалось открыть настройки текущей папки.
      </div>
    {/if}

    <div class="flex justify-end gap-2">
      <Button color="ghost" on:click={handleClose}>Закрыть</Button>
    </div>
  </div>
</Modal>
