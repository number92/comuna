<script lang="ts">
  import type { SiteUser } from '$lib/siteAuth'
  import { Button, TextInput } from 'mono-svelte'
  import { createEventDispatcher } from 'svelte'

  export let siteUser: SiteUser | null = null
  export let displayName = ''
  export let avatarUrl = ''
  export let saving = false
  export let uploading = false

  const dispatch = createEventDispatcher<{
    avatarSelected: File
    clearAvatar: void
    save: void
  }>()

  let fileInput: HTMLInputElement | null = null

  const onFileChange = (event: Event) => {
    const input = event.currentTarget as HTMLInputElement | null
    const file = input?.files?.[0]
    if (!file) return
    dispatch('avatarSelected', file)
    if (input) input.value = ''
  }
</script>

<div class="flex flex-col gap-4">
  <div class="text-sm text-slate-500 dark:text-zinc-400">
    Это профиль, который отображается на сайте в комментариях и на странице пользователя.
  </div>

  <div class="flex flex-col sm:flex-row gap-4 items-start">
    <div class="w-20 h-20 rounded-full overflow-hidden border border-slate-200 dark:border-zinc-800 bg-slate-100 dark:bg-zinc-800 shrink-0">
      {#if avatarUrl}
        <img src={avatarUrl} alt="Аватар профиля" class="w-full h-full object-cover" />
      {:else}
        <div class="w-full h-full grid place-items-center text-lg font-semibold text-slate-500 dark:text-zinc-400">
          {(siteUser?.display_name || siteUser?.username || '?').slice(0, 1).toUpperCase()}
        </div>
      {/if}
    </div>

    <div class="flex-1 min-w-0 flex flex-col gap-3">
      <input
        bind:this={fileInput}
        type="file"
        accept="image/*"
        class="hidden"
        on:change={onFileChange}
      />

      <TextInput
        bind:value={displayName}
        label="Имя отображаемое на сайте"
        placeholder={`Например: ${siteUser?.username ?? ''}`}
        maxLength={120}
      />

      <div class="flex flex-wrap items-center gap-2">
        <Button
          size="sm"
          on:click={() => fileInput?.click()}
          disabled={saving || uploading}
        >
          {avatarUrl ? 'Заменить аватарку' : 'Загрузить аватарку'}
        </Button>
        {#if avatarUrl}
          <Button
            size="sm"
            color="ghost"
            on:click={() => dispatch('clearAvatar')}
            disabled={saving || uploading}
          >
            Убрать аватарку
          </Button>
        {/if}
        {#if uploading}
          <span class="text-xs text-slate-500 dark:text-zinc-400">Загрузка...</span>
        {/if}
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <Button on:click={() => dispatch('save')} disabled={saving || uploading}>
          {saving ? 'Сохраняем...' : 'Сохранить'}
        </Button>
        <div class="text-xs text-slate-500 dark:text-zinc-400">
          Логин @{siteUser?.username ?? ''} не меняется и используется для входа.
        </div>
      </div>
    </div>
  </div>
</div>
