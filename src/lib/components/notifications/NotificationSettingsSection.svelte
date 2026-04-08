<script lang="ts">
  import TelegramConnectionCard from '$lib/components/telegram/TelegramConnectionCard.svelte'
  import type { SiteNotificationEventSetting } from '$lib/siteAuth'
  import { Button } from 'mono-svelte'
  import { createEventDispatcher } from 'svelte'

  export let events: SiteNotificationEventSetting[] = []
  export let loading = false
  export let saving = false
  export let dirty = false
  export let telegramLinked = false
  export let telegramUsername = ''
  export let telegramFirstName = ''

  const dispatch = createEventDispatcher<{
    save: void
    toggle: { index: number; channel: 'site' | 'telegram'; value: boolean }
  }>()

  const handleToggle = (
    index: number,
    channel: 'site' | 'telegram',
    event: Event
  ) => {
    const target = event.currentTarget as HTMLInputElement | null
    dispatch('toggle', {
      index,
      channel,
      value: Boolean(target?.checked),
    })
  }
</script>

<div class="flex flex-col gap-4">
  <div class="text-sm text-slate-500 dark:text-zinc-400">
    Выберите, для каких событий показывать уведомления в колокольчике на сайте и
    отправлять сообщения в Telegram-бот.
  </div>

  <TelegramConnectionCard
    linked={telegramLinked}
    username={telegramUsername}
    firstName={telegramFirstName}
  />

  {#if loading && !events.length}
    <div class="text-sm text-slate-500 dark:text-zinc-400">
      Загружаем настройки оповещений...
    </div>
  {:else if events.length}
    <div class="overflow-x-auto rounded-xl border border-slate-200 dark:border-zinc-800">
      <table class="w-full min-w-[680px] text-sm">
        <thead class="bg-slate-50 dark:bg-zinc-900/70">
          <tr class="text-left">
            <th class="px-4 py-3 font-medium text-slate-700 dark:text-zinc-200">Событие</th>
            <th class="px-4 py-3 font-medium text-center text-slate-700 dark:text-zinc-200 w-28">На сайте</th>
            <th class="px-4 py-3 font-medium text-center text-slate-700 dark:text-zinc-200 w-28">Telegram</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 dark:divide-zinc-800">
          {#each events as event, index}
            <tr class="align-top">
              <td class="px-4 py-3">
                <div class="font-medium text-slate-900 dark:text-zinc-100">
                  {event.title}
                </div>
                {#if event.description}
                  <div class="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                    {event.description}
                  </div>
                {/if}
              </td>
              <td class="px-4 py-3 text-center">
                <input
                  type="checkbox"
                  class="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-900"
                  checked={event.site_enabled}
                  on:change={(event) => handleToggle(index, 'site', event)}
                />
              </td>
              <td class="px-4 py-3 text-center">
                <input
                  type="checkbox"
                  class="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-900"
                  checked={event.telegram_enabled}
                  on:change={(event) => handleToggle(index, 'telegram', event)}
                />
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="flex flex-wrap items-center gap-2">
      <Button on:click={() => dispatch('save')} disabled={saving || !dirty}>
        {saving ? 'Сохраняем...' : 'Сохранить настройки'}
      </Button>
      <div class="text-xs text-slate-500 dark:text-zinc-400">
        Изменения применяются ко всем будущим уведомлениям.
      </div>
    </div>
  {:else}
    <div class="text-sm text-slate-500 dark:text-zinc-400">
      Список событий уведомлений пока пуст.
    </div>
  {/if}
</div>
