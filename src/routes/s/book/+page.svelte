<script lang="ts">
  import { onMount } from 'svelte'
  import { Button, toast } from 'mono-svelte'
  import {
    buildSpecialBookReminderUrl,
    buildSpecialBookStatusUrl,
    buildSpecialBookSubmitUrl,
    buildSpecialBookWordsUrl,
  } from '$lib/api/backend'
  import LoginModal from '$lib/components/auth/LoginModal.svelte'
  import PostComments from '$lib/components/site/PostComments.svelte'
  import { siteToken, siteUser } from '$lib/siteAuth'
  import {
    ArrowPath,
    Bell,
    Check,
    Clock,
    Icon,
    LockClosed,
  } from 'svelte-hero-icons'

  type BookWord = {
    id: number
    position: number
    word: string
    created_at: string
    submitted_by: {
      id: number
      username: string
    }
  }

  type BookStatus = {
    ok: boolean
    max_words: number
    total_words: number
    remaining_words: number
    can_submit: boolean
    submit_block_reason?: string
    next_available_at?: string | null
    telegram_linked?: boolean
    vk_linked?: boolean
    has_social_identity?: boolean
    reminder?: {
      scheduled: boolean
      scheduled_at?: string | null
      sent_at?: string | null
    }
    discussion_post?: {
      id: number
      comments_count: number
    }
  }

  const PAGE_LIMIT = 700
  const WORD_LIMIT = 30

  let status: BookStatus | null = null
  let words: BookWord[] = []
  let loading = true
  let wordsLoading = false
  let submitLoading = false
  let reminderLoading = false
  let error = ''
  let word = ''
  let authOpen = false
  let authInitialMode: 'login' | 'signup' = 'signup'
  let loadedOffset = 0
  let lastToken: string | null = null

  const authHeaders = (): Record<string, string> =>
    $siteToken ? { Authorization: `Bearer ${$siteToken}` } : {}

  const normalizeInput = (value: string) =>
    value
      .replace(/\s+/g, '')
      .replace(/[^\p{L}]/gu, '')
      .slice(0, WORD_LIMIT)

  const formatNumber = (value?: number | null) =>
    new Intl.NumberFormat('ru-RU').format(value ?? 0)

  const formatDate = (value?: string | null) => {
    if (!value) return ''
    try {
      return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        hour: '2-digit',
        minute: '2-digit',
      }).format(new Date(value))
    } catch {
      return value
    }
  }

  async function loadStatus() {
    const response = await fetch(buildSpecialBookStatusUrl(), {
      credentials: 'include',
      headers: authHeaders(),
    })
    const data = await response.json()
    if (!response.ok || !data?.ok) {
      throw new Error(data?.error || 'Не удалось загрузить проект')
    }
    status = data
  }

  async function loadWords(options: { reset?: boolean } = {}) {
    wordsLoading = true
    const offset = options.reset ? 0 : loadedOffset
    try {
      const response = await fetch(buildSpecialBookWordsUrl({ offset, limit: PAGE_LIMIT }), {
        cache: 'no-store',
      })
      const data = await response.json()
      if (!response.ok || !data?.ok) {
        throw new Error(data?.error || 'Не удалось загрузить слова')
      }
      const nextWords = (data.words ?? []) as BookWord[]
      words = options.reset ? nextWords : [...words, ...nextWords]
      loadedOffset = offset + nextWords.length
      if (status) {
        status = { ...status, total_words: data.total_words ?? status.total_words }
      }
    } catch (err) {
      toast({ content: (err as Error)?.message || 'Не удалось загрузить слова', type: 'error' })
    }
    wordsLoading = false
  }

  async function loadProject() {
    loading = true
    error = ''
    try {
      await loadStatus()
      await loadWords({ reset: true })
    } catch (err) {
      error = (err as Error)?.message || 'Не удалось загрузить проект'
    }
    loading = false
  }

  async function submitWord() {
    if (!$siteToken || !$siteUser) {
      authInitialMode = 'signup'
      authOpen = true
      return
    }
    if (!$siteUser.telegram_linked && !$siteUser.vk_linked) {
      authInitialMode = 'login'
      authOpen = true
      toast({ content: 'Привяжите Telegram или VK, чтобы добавить слово.', type: 'info' })
      return
    }
    const cleanWord = normalizeInput(word)
    word = cleanWord
    if (!cleanWord) {
      toast({ content: 'Введите одно слово', type: 'info' })
      return
    }

    submitLoading = true
    try {
      const response = await fetch(buildSpecialBookSubmitUrl(), {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(),
        },
        body: JSON.stringify({ word: cleanWord }),
      })
      const data = await response.json()
      if (!response.ok || !data?.ok) {
        status = status
          ? {
              ...status,
              can_submit: Boolean(data?.can_submit),
              next_available_at: data?.next_available_at ?? status.next_available_at,
              submit_block_reason: data?.submit_block_reason ?? status.submit_block_reason,
              telegram_linked: data?.telegram_linked ?? status.telegram_linked,
              vk_linked: data?.vk_linked ?? status.vk_linked,
              has_social_identity: data?.has_social_identity ?? status.has_social_identity,
              reminder: data?.reminder ?? status.reminder,
            }
          : status
        throw new Error(data?.error || 'Не удалось добавить слово')
      }
      word = ''
      toast({ content: `Слово добавлено под номером ${formatNumber(data.word?.position)}`, type: 'success' })
      await loadProject()
    } catch (err) {
      toast({ content: (err as Error)?.message || 'Не удалось добавить слово', type: 'error' })
    }
    submitLoading = false
  }

  async function scheduleReminder() {
    if (!$siteToken || !$siteUser) {
      authInitialMode = 'login'
      authOpen = true
      return
    }
    if (!$siteUser.telegram_linked) {
      authInitialMode = 'login'
      authOpen = true
      toast({ content: 'Привяжите Telegram, чтобы получить напоминание.', type: 'info' })
      return
    }

    reminderLoading = true
    try {
      const response = await fetch(buildSpecialBookReminderUrl(), {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(),
        },
      })
      const data = await response.json()
      if (!response.ok || !data?.ok) {
        status = status
          ? {
              ...status,
              reminder: data?.reminder ?? status.reminder,
              can_submit: Boolean(data?.can_submit),
              next_available_at: data?.next_available_at ?? status.next_available_at,
            }
          : status
        if (data?.requires_telegram) {
          authInitialMode = 'login'
          authOpen = true
        }
        throw new Error(data?.error || 'Не удалось поставить напоминание')
      }
      status = data as BookStatus
      toast({ content: 'Напоминание в Telegram включено', type: 'success' })
    } catch (err) {
      toast({ content: (err as Error)?.message || 'Не удалось поставить напоминание', type: 'error' })
    }
    reminderLoading = false
  }

  $: progressPercent = status
    ? Math.min(100, Math.max(0, (status.total_words / status.max_words) * 100))
    : 0
  $: displayTotalWords = status?.total_words ?? 0
  $: displayMaxWords = status?.max_words ?? 185000
  $: bookText = words.map((item) => item.word).join(' ')
  $: canLoadMore = Boolean(status && words.length < status.total_words)
  $: submitDisabled = submitLoading || loading || Boolean(status && !status.can_submit)
  $: needsSocialLink = Boolean($siteUser && !$siteUser.telegram_linked && !$siteUser.vk_linked)
  $: canShowReminder = Boolean($siteUser && status?.next_available_at)
  $: reminderScheduled = Boolean(status?.reminder?.scheduled)

  $: if ($siteToken !== lastToken) {
    lastToken = $siteToken
    if (!loading) {
      loadStatus().catch((err) => {
        error = (err as Error)?.message || 'Не удалось обновить статус'
      })
    }
  }

  onMount(loadProject)
</script>

<svelte:head>
  <title>Книга сообщества интернет — Tambur</title>
  <meta
    name="description"
    content="Мы люди из интернет-сообщества вместе напишем книгу о том, что думаем, видим, чувствуем."
  />
  <link rel="canonical" href="/s/book" />
</svelte:head>

<LoginModal bind:open={authOpen} initialMode={authInitialMode} />

<section class="book-page">
  <div class="hero-band">
    <div class="hero-inner">
      <div class="hero-copy">
        <h1>Книга сообщества интернет</h1>
        <p>
          Мы люди из интернет-сообщества вместе напишем книгу о том, что думаем,
          видим, чувствуем. После завершения книга будет отцензурирована и выпущена
          в электронном виде доступном бесплатно каждому и в печатном виде. Каждый
          может добавлять только одно слово в сутки.
        </p>
      </div>

      <div class="book-counter-panel">
        <div class="counter-title">Объем книги</div>
        <div class="counter-value">
          {formatNumber(displayTotalWords)}
          <span>из</span>
          {formatNumber(displayMaxWords)}
        </div>
        <div class="progress-track" aria-label="Прогресс книги">
          <span style={`width: ${progressPercent}%`}></span>
        </div>
        {#if status?.next_available_at}
          <div class="cooldown">
            <Icon src={Clock} size="16" mini />
            Следующее слово: {formatDate(status.next_available_at)}
          </div>
        {/if}
        {#if needsSocialLink}
          <div class="counter-note">
            Чтобы добавить слово, привяжите Telegram или VK к учетной записи.
          </div>
        {/if}
      </div>
    </div>
  </div>

  <div class="book-inner">
    {#if error}
      <p class="error">{error}</p>
    {:else if loading}
      <div class="loading-line">
        <Icon src={ArrowPath} size="18" mini />
        Загрузка
      </div>
    {:else}
      <section class="book-sheet" aria-label="Текст книги">
        <div class="sheet-head">
          <span>Текущая версия</span>
          <span>{formatNumber(displayTotalWords)} из {formatNumber(displayMaxWords)}</span>
        </div>
        <div class="book-text">
          {#if bookText}
            <span>{bookText}</span>
          {:else}
            <span class="empty-book">Книга пока пустая.</span>
          {/if}
          <form on:submit|preventDefault={submitWord} class="inline-word-form">
            <input
              bind:value={word}
              on:input={(event) => (word = normalizeInput((event.currentTarget as HTMLInputElement).value))}
              on:focus={() => {
                if (!$siteUser) {
                  authInitialMode = 'signup'
                  authOpen = true
                }
              }}
              placeholder="слово"
              maxlength={WORD_LIMIT}
              autocomplete="off"
              disabled={submitLoading || loading}
              aria-label="Добавить слово в книгу"
            />
            {#if !$siteUser}
              <button
                type="button"
                class="inline-submit"
                aria-label="Войти, чтобы добавить слово"
                on:click={() => {
                  authInitialMode = 'signup'
                  authOpen = true
                }}
              >
                <Icon src={LockClosed} size="16" mini />
              </button>
            {:else if needsSocialLink}
              <button
                type="button"
                class="inline-submit"
                aria-label="Привязать Telegram или VK"
                on:click={() => {
                  authInitialMode = 'login'
                  authOpen = true
                }}
              >
                <Icon src={LockClosed} size="16" mini />
              </button>
            {:else}
              <button
                type="submit"
                class="inline-submit"
                aria-label="Добавить слово"
                disabled={submitDisabled}
              >
                {#if submitLoading}
                  <Icon src={ArrowPath} size="16" mini />
                {:else}
                  <Icon src={Check} size="16" mini />
                {/if}
              </button>
            {/if}
          </form>
        </div>
        {#if canShowReminder}
          <div class="reminder-row">
            {#if reminderScheduled}
              <Button color="secondary" disabled>
                <Icon src={Bell} size="18" mini slot="prefix" />
                Напоминание включено
              </Button>
            {:else if $siteUser?.telegram_linked}
              <Button color="secondary" loading={reminderLoading} disabled={reminderLoading} on:click={scheduleReminder}>
                <Icon src={Bell} size="18" mini slot="prefix" />
                Напомнить через 24 часа
              </Button>
            {:else}
              <Button color="secondary" disabled={reminderLoading} on:click={scheduleReminder}>
                <Icon src={Bell} size="18" mini slot="prefix" />
                Привязать Telegram для напоминания
              </Button>
            {/if}
          </div>
        {/if}
        {#if canLoadMore}
          <div class="load-more">
            <Button color="secondary" loading={wordsLoading} disabled={wordsLoading} on:click={() => loadWords()}>
              Загрузить еще
            </Button>
          </div>
        {/if}
      </section>

      {#if status?.discussion_post?.id}
        <PostComments postId={status.discussion_post.id} postAuthor="tambur-book" />
      {/if}
    {/if}
  </div>
</section>

<style>
  .book-page {
    min-height: 100vh;
    background: #f6f1e9;
    color: #1f2933;
  }

  .hero-band {
    border-bottom: 1px solid #ded6c9;
    background:
      linear-gradient(90deg, rgba(31, 41, 51, 0.06) 1px, transparent 1px),
      linear-gradient(#fbf8f2, #f0e7da);
    background-size: 28px 28px, auto;
  }

  .hero-inner,
  .book-inner {
    width: min(1120px, calc(100vw - 32px));
    margin: 0 auto;
  }

  .hero-inner {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
    gap: 48px;
    align-items: end;
    padding: 64px 0 42px;
  }

  h1 {
    margin: 0;
    max-width: 720px;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: clamp(46px, 8vw, 92px);
    line-height: 0.94;
    letter-spacing: 0;
  }

  .hero-copy p {
    max-width: 700px;
    margin: 24px 0 0;
    color: #374151;
    font-size: 18px;
    line-height: 1.65;
  }

  .book-counter-panel {
    border: 1px solid #d6c8b6;
    border-radius: 8px;
    background: #fffdf8;
    box-shadow: 0 18px 50px rgba(49, 37, 21, 0.14);
    padding: 20px;
  }

  .sheet-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    color: #5b6470;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .counter-title {
    color: #6b5f51;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .counter-value {
    margin-top: 8px;
    color: #1f2933;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: clamp(32px, 5vw, 54px);
    line-height: 1;
    letter-spacing: 0;
  }

  .counter-value span {
    margin: 0 8px;
    color: #8a7a67;
    font-family: inherit;
    font-size: 0.46em;
    font-style: italic;
  }

  .progress-track {
    height: 10px;
    margin-top: 18px;
    overflow: hidden;
    border: 1px solid #d6c8b6;
    border-radius: 999px;
    background: #e7dccd;
  }

  .progress-track span {
    display: block;
    height: 100%;
    background: #2f6f59;
  }

  .cooldown,
  .loading-line {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    color: #6b7280;
    font-size: 14px;
  }

  .counter-note {
    margin-top: 14px;
    color: #7c5f2f;
    font-size: 14px;
    line-height: 1.45;
  }

  .book-inner {
    padding: 36px 0 64px;
  }

  .book-sheet {
    border: 1px solid #d8cbb9;
    border-radius: 8px;
    background: #fffdf8;
    padding: 28px;
  }

  .book-text {
    min-height: 260px;
    margin-top: 22px;
    color: #1f2933;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: clamp(22px, 3vw, 34px);
    line-height: 1.7;
    overflow-wrap: anywhere;
  }

  .empty-book {
    color: #8a7a67;
    font-style: italic;
  }

  .inline-word-form {
    display: inline-flex;
    width: auto;
    align-items: center;
    gap: 4px;
    margin-left: 8px;
    vertical-align: baseline;
  }

  .inline-word-form input {
    width: 7.2em;
    min-width: 92px;
    max-width: 42vw;
    border: 0;
    border-bottom: 2px solid #b79d7c;
    border-radius: 0;
    background: rgba(255, 255, 255, 0.58);
    color: #1f2933;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 0.86em;
    letter-spacing: 0;
    line-height: 1.25;
    padding: 2px 4px 3px;
    outline: none;
  }

  .inline-word-form input:focus {
    border-bottom-color: #2f6f59;
    background: #fffdf8;
  }

  .inline-word-form input::placeholder {
    color: #a18f77;
    font-style: italic;
  }

  .inline-submit {
    display: inline-flex;
    width: 28px;
    height: 28px;
    align-items: center;
    justify-content: center;
    border: 1px solid #2f6f59;
    border-radius: 999px;
    background: #2f6f59;
    color: #fffdf8;
    vertical-align: middle;
    transition:
      background 0.15s ease,
      border-color 0.15s ease,
      opacity 0.15s ease;
  }

  .inline-submit:hover:not(:disabled) {
    border-color: #245946;
    background: #245946;
  }

  .inline-submit:disabled {
    cursor: default;
    opacity: 0.45;
  }

  .load-more {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }

  .reminder-row {
    display: flex;
    justify-content: flex-start;
    margin-top: 20px;
  }

  .error {
    color: #b42318;
  }

  :global(.book-page #comments) {
    margin-top: 42px;
    color: #111827;
  }

  @media (max-width: 820px) {
    .hero-inner {
      grid-template-columns: 1fr;
      gap: 28px;
      padding-top: 42px;
    }

    .book-sheet {
      padding: 20px;
    }

    .inline-word-form {
      margin-left: 4px;
    }
  }
</style>
