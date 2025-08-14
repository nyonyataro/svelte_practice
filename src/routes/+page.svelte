<script lang="ts">
    let selectedFile = $state<FileList>();
    let fileUrl = $derived(
        selectedFile ? URL.createObjectURL(selectedFile[0]) : "",
    );
</script>

<h1>Sample</h1>
<label for="input_pic">画像をアップロード</label><br />
<input
    bind:files={selectedFile}
    type="file"
    id="input_pic"
    name="input_pic"
    required
    accept="image/*"
/>
<br />
<br />
<button id="submit"> 変換実施 </button><br />
{#if selectedFile}
    <p>fileURL：{fileUrl}</p>
    <img src={fileUrl} alt="Uploaded" style="max-width: 100%;" />
{/if}
