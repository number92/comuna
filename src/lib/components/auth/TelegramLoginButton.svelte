<script lang="ts">
  import TelegramLoginButton from '$lib/components/telegram/TelegramLoginButton.svelte'

  export let onSuccess: (() => void) | null = null
  export let label = 'Продолжить с Telegram'
  export let helperText = ''
  export let active = true
</script>

<TelegramLoginButton {onSuccess} {label} {helperText} {active} />
