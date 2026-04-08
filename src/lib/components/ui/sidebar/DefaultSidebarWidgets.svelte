<script lang="ts">
  import TopAuthorsSidebar from '$lib/components/ratings/TopAuthorsSidebar.svelte'
  import KeyboardShortcutsHint from '$lib/components/ui/sidebar/KeyboardShortcutsHint.svelte'
  import RecentComments from '$lib/components/ui/sidebar/RecentComments.svelte'

  export let keyboardShortcutsHintEnabled = false
</script>

<div class="flex flex-col gap-4">
  <KeyboardShortcutsHint enabled={keyboardShortcutsHintEnabled} />
  <TopAuthorsSidebar />
  <div class="h-px bg-slate-200 dark:bg-zinc-800"></div>
  <RecentComments />
</div>
