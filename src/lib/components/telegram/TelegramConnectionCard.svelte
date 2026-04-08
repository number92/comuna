<script lang="ts">
  export let linked = false
  export let username = ''
  export let firstName = ''
</script>

<div class="rounded-xl border border-slate-200 bg-slate-50/60 p-3 dark:border-zinc-800 dark:bg-zinc-900/40">
  <div class="text-sm font-medium text-slate-900 dark:text-zinc-100">
    Telegram: {linked ? 'подключен' : 'не подключен'}
  </div>
  <div class="mt-1 text-xs text-slate-500 dark:text-zinc-400">
    {#if linked}
      {#if username}
        Аккаунт: @{username}
      {:else if firstName}
        Аккаунт: {firstName}
      {:else}
        Telegram-аккаунт привязан к профилю.
      {/if}
    {:else}
      Привяжите Telegram через вход/авторизацию Telegram, чтобы бот мог присылать оповещения.
    {/if}
  </div>
</div>
