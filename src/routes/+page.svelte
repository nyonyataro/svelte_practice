<script lang="ts">
    // 既存の state と互換（あなたの前コードに合わせてます）
    let selectedFile = $state<FileList>();
    let userPrompt = $state("");
    let derivedFileUrl = $derived(
        selectedFile?.[0] ? URL.createObjectURL(selectedFile[0]) : "",
    );
    let isLoading = $state(false);
    let generatedImageUrl = $state("");
    let errorMessage = $state("");
    import { PUBLIC_API_BASE } from "$env/static/public";
    const API_URL = `${PUBLIC_API_BASE ?? "http://127.0.0.1:8000"}/generate`;
    // 追加: UI/UX用の状態
    let fileInput: HTMLInputElement | null = null;
    let uploadError = $state<string | null>(null);
    const MAX_MB = 5;
    const ACCEPT_MIME = ["image/png", "image/jpeg", "image/webp"];

    const PRESETS = [
        "白背景に商品を中央配置",
        "大理石テーブル上で上品に",
        "自然光・柔らかい影を追加",
        "ダーク背景＋淡いリムライト",
    ];

    function formatBytes(n: number) {
        if (n < 1024) return `${n} B`;
        if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
        return `${(n / (1024 * 1024)).toFixed(1)} MB`;
    }

    function validateFile(file: File): string | null {
        if (!ACCEPT_MIME.includes(file.type))
            return "PNG / JPEG / WEBP のみ対応です。";
        if (file.size > MAX_MB * 1024 * 1024)
            return `ファイルサイズは最大 ${MAX_MB}MB までです。`;
        return null;
    }

    function setFileList(files: FileList | null) {
        uploadError = null;
        if (!files || !files[0]) return;
        const e = validateFile(files[0]);
        if (e) {
            uploadError = e;
            selectedFile = undefined as any;
            return;
        }
        selectedFile = files as any;
    }

    function clearSelected() {
        selectedFile = undefined as any;
        uploadError = null;
        if (fileInput) fileInput.value = "";
    }

    function applyPreset(p: string) {
        userPrompt = userPrompt ? `${userPrompt}\n- ${p}` : `- ${p}`;
    }

    // ダウンロード（生成結果）
    function downloadImage() {
        if (!generatedImageUrl) return;
        const a = document.createElement("a");
        a.href = generatedImageUrl;
        a.download = "generated.png";
        document.body.appendChild(a);
        a.click();
        a.remove();
    }

    // ① 共通補足文（日本語で端的に）
    const COMMON_CONTEXT = `
        以下のアップロード画像を、テキストエリアに記載の条件を踏まえて編集してください。
        - 必要最小限の変更で要望を満たす
        - 可能なら縦横比と被写体の識別性を維持
        出力: 単一の完成画像
        `.trim();

    // ② 送信直前で合成（空欄フォールバックも）
    async function handleClick() {
        if (!selectedFile?.[0]) {
            errorMessage = "ファイルが選択されていません。";
            return;
        }
        isLoading = true;
        generatedImageUrl = "";
        errorMessage = "";

        try {
            const fullPrompt = `${COMMON_CONTEXT}\n\n【ユーザーの要望】\n${(userPrompt ?? "").trim() || "自然な色補正と軽いシャープネス調整をしてください。"}`;

            const formData = new FormData();
            formData.append("file", selectedFile[0]);
            formData.append("prompt", fullPrompt);

            const res = await fetch(API_URL, {
                method: "POST",
                body: formData,
            });
            if (!res.ok) {
                const e = await res.json().catch(() => ({}));
                throw new Error(
                    e.error?.message || "APIリクエストに失敗しました。",
                );
            }
            const data = await res.json();
            if (data.image_url) {
                generatedImageUrl = data.image_url;
            } else {
                throw new Error("画像データが返されませんでした。");
            }
        } catch (err) {
            console.error(err);
            errorMessage =
                (err as Error).message ||
                "画像の生成中に不明なエラーが発生しました。";
        } finally {
            isLoading = false;
        }
    }
</script>

<main class="min-h-screen bg-gradient-to-b from-white to-gray-50">
    <!-- ヘッダー -->
    <header class="container mx-auto px-4 pt-8 pb-6 md:pt-12 md:pb-8">
        <h1
            class="text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900"
        >
            AI画像ジェネレーター
        </h1>
        <p class="mt-2 text-gray-600">
            画像をアップロードし、どのように変更したいか指示してください。
        </p>
    </header>

    <!-- 2カラム -->
    <section
        class="container mx-auto px-4 pb-12 grid grid-cols-1 lg:grid-cols-2 gap-8"
    >
        <!-- 左：入力 -->
        <div class="space-y-6">
            <!-- アップロードカード -->
            <div class="rounded-2xl border bg-white shadow-sm p-5 md:p-6">
                <h2 class="text-base font-semibold text-gray-800 mb-3">
                    1. 画像をアップロード
                </h2>

                <!-- ドロップゾーン -->
                <div
                    class="group relative rounded-xl border border-dashed border-gray-300 bg-white/70 p-6
                 hover:border-violet-400 hover:bg-violet-50/60 transition-colors cursor-pointer"
                    role="button"
                    tabindex="0"
                    onclick={() => fileInput?.click()}
                    onkeydown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            fileInput?.click();
                        }
                    }}
                    ondragover={(e) => e.preventDefault()}
                    ondrop={(e) => {
                        e.preventDefault();
                        const files = e.dataTransfer?.files ?? null;
                        setFileList(files as any);
                    }}
                    aria-label="画像をドラッグ&ドロップ、またはクリックして選択"
                >
                    <input
                        bind:this={fileInput}
                        bind:files={selectedFile}
                        type="file"
                        id="input_pic"
                        name="input_pic"
                        accept={ACCEPT_MIME.join(",")}
                        class="sr-only"
                        disabled={isLoading}
                        onchange={(e) =>
                            setFileList((e.target as HTMLInputElement).files)}
                    />

                    <div class="flex items-center gap-3 text-gray-700">
                        <div
                            class="grid h-10 w-10 place-items-center rounded-lg bg-violet-100 text-violet-700 font-bold"
                        >
                            ↑
                        </div>
                        <div>
                            <p class="font-medium text-gray-800">
                                ドラッグ&ドロップ
                            </p>
                            <p class="text-sm text-gray-500">
                                またはクリックして選択（PNG / JPEG / WEBP, {MAX_MB}MBまで）
                            </p>
                        </div>
                    </div>

                    {#if selectedFile?.[0]}
                        <p class="mt-3 text-xs text-gray-500">
                            {selectedFile[0].name}・{formatBytes(
                                selectedFile[0].size,
                            )}
                        </p>
                    {/if}
                </div>

                {#if uploadError}
                    <div
                        class="mt-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3"
                    >
                        {uploadError}
                    </div>
                {/if}

                {#if derivedFileUrl}
                    <div
                        class="mt-4 p-4 border rounded-xl bg-gray-50 flex justify-center"
                    >
                        <img
                            src={derivedFileUrl}
                            alt="アップロード画像のプレビュー"
                            class="w-full h-auto object-contain
                     max-w-[min(90%,240px)] sm:max-w-[min(80%,320px)] lg:max-w-[min(70%,400px)]
                     max-h-[70vh] rounded-md shadow"
                            loading="lazy"
                        />
                    </div>

                    <div class="mt-3 flex items-center gap-3">
                        <button
                            type="button"
                            onclick={clearSelected}
                            class="px-3 py-2 text-sm rounded-md border text-gray-700 hover:bg-gray-50"
                            >画像をクリア</button
                        >
                    </div>
                {/if}
            </div>

            <!-- プロンプトカード -->
            <div class="rounded-2xl border bg-white shadow-sm p-5 md:p-6">
                <h2 class="text-base font-semibold text-gray-800 mb-3">
                    2. どのように変更しますか？
                </h2>

                <!-- プリセット -->
                <div class="flex flex-wrap gap-2 mb-3">
                    {#each PRESETS as p}
                        <button
                            type="button"
                            onclick={() => applyPreset(p)}
                            class="px-3 py-1.5 text-sm rounded-full border border-violet-200 text-violet-700 bg-violet-50 hover:bg-violet-100"
                            >{p}</button
                        >
                    {/each}
                </div>

                <label for="user_prompt" class="sr-only">編集内容</label>
                <textarea
                    id="user_prompt"
                    bind:value={userPrompt}
                    rows="5"
                    placeholder="例：白背景で商品を中央に配置し、柔らかい自然光と薄い影を追加。"
                    class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-violet-500 focus:border-violet-500"
                    disabled={isLoading}
                ></textarea>

                <div
                    class="mt-3 flex items-center justify-between text-sm text-gray-500"
                >
                    <span>{userPrompt.length} 文字</span>
                    <span class="hidden sm:block"
                        >ヒント: 箇条書きで具体的に指示すると安定します</span
                    >
                </div>

                <div class="mt-4 flex gap-3">
                    <button
                        id="submit"
                        onclick={handleClick}
                        disabled={isLoading || !selectedFile || !!uploadError}
                        class="flex-1 bg-violet-600 text-white font-semibold py-3 rounded-lg
                   hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500
                   disabled:bg-gray-300 disabled:text-white/80 disabled:cursor-not-allowed transition-colors"
                    >
                        {#if isLoading}生成中…{:else}画像生成を実行{/if}
                    </button>

                    <button
                        type="button"
                        onclick={() => {
                            userPrompt = "";
                        }}
                        class="px-4 py-3 rounded-lg border text-gray-700 hover:bg-gray-50"
                        >入力クリア</button
                    >
                </div>

                {#if errorMessage}
                    <div
                        class="mt-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3"
                    >
                        エラー: {errorMessage}
                    </div>
                {/if}
            </div>
        </div>

        <!-- 右：結果 -->
        <div
            class="lg:sticky lg:top-6 h-fit rounded-2xl border bg-white shadow-sm p-5 md:p-6"
        >
            <h2 class="text-base font-semibold text-gray-800 mb-3">
                3. 生成結果
            </h2>

            {#if isLoading}
                <!-- スケルトン -->
                <div class="animate-pulse">
                    <div class="h-6 w-40 bg-gray-200 rounded mb-4"></div>
                    <div
                        class="w-full aspect-video bg-gray-200 rounded-xl"
                    ></div>
                </div>
            {:else if generatedImageUrl}
                <div class="space-y-4">
                    <div class="flex justify-center">
                        <img
                            src={generatedImageUrl}
                            alt="生成された画像"
                            class="w-full h-auto object-contain
                     max-w-[min(90%,240px)] sm:max-w-[min(80%,320px)] lg:max-w-[min(70%,400px)]
                     max-h-[70vh] rounded-md shadow"
                        />
                    </div>
                    <div class="flex gap-3">
                        <button
                            type="button"
                            onclick={downloadImage}
                            class="flex-1 px-4 py-2 rounded-lg border text-gray-700 hover:bg-gray-50"
                            >ダウンロード</button
                        >
                        <button
                            type="button"
                            onclick={() => {
                                generatedImageUrl = "";
                            }}
                            class="px-4 py-2 rounded-lg border text-gray-700 hover:bg-gray-50"
                            >結果をクリア</button
                        >
                    </div>
                </div>
            {:else}
                <p class="text-gray-500">
                    ここに生成された画像が表示されます。
                </p>
            {/if}
        </div>
    </section>
</main>
