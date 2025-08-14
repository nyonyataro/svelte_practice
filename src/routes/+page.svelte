<script lang="ts">
    // Svelteのリアクティブ機能
    let selectedFile = $state<FileList>();
    let userPrompt = $state("");
    let derivedFileUrl = $derived(
        selectedFile?.[0] ? URL.createObjectURL(selectedFile[0]) : "",
    );
    let isLoading = $state(false); // API通信中のロード状態を管理
    let generatedImageUrl = $state(""); // 生成された画像のURLを保存
    let errorMessage = $state(""); // エラーメッセージを保存

    const API_URL = "http://127.0.0.1:8000/generate";

    /**
     * FileオブジェクトをBase64形式の文字列に変換するヘルパー関数
     */
    function toBase64(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () =>
                resolve((reader.result as string).split(",")[1]);
            reader.onerror = (error) => reject(error);
        });
    }

    /**
     * 「変換実施」ボタンがクリックされたときに実行される非同期関数
     */
    const handleClick = async () => {
        if (!selectedFile?.[0]) {
            errorMessage = "ファイルが選択されていません。";
            return;
        }

        isLoading = true;
        generatedImageUrl = "";
        errorMessage = "";

        try {
            const formData = new FormData();
            formData.append("file", selectedFile[0]);
            formData.append("prompt", userPrompt);

            const response = await fetch(API_URL, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.error?.message || "APIリクエストに失敗しました。",
                );
            }

            const data = await response.json();

            if (data.image_url) {
                generatedImageUrl = data.image_url;
            } else {
                console.log(
                    "API Response Data:",
                    JSON.stringify(data, null, 2),
                );
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
    };
</script>

<main class="container mx-auto p-4 md:p-8 font-sans">
    <header class="mb-8">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-800">
            AI画像ジェネレーター
        </h1>
        <p class="text-gray-600 mt-2">
            画像をアップロードし、どのように変更したいか指示してください。
        </p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- 左側：入力エリア -->
        <div class="space-y-6">
            <div>
                <label
                    for="input_pic"
                    class="block text-lg font-medium text-gray-700 mb-2"
                    >1. 元になる画像をアップロード</label
                >
                <input
                    bind:files={selectedFile}
                    type="file"
                    id="input_pic"
                    name="input_pic"
                    required
                    accept="image/*"
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
                    disabled={isLoading}
                />
            </div>

            {#if derivedFileUrl}
                <div class="p-4 border rounded-lg bg-gray-50">
                    <h3 class="font-semibold text-gray-700 mb-2">プレビュー</h3>
                    <img
                        src={derivedFileUrl}
                        alt="Uploaded"
                        class="max-w-full h-auto rounded-md shadow-md"
                    />
                </div>
            {/if}

            <div>
                <label
                    for="user_prompt"
                    class="block text-lg font-medium text-gray-700 mb-2"
                    >2. どのように変更しますか？</label
                >
                <textarea
                    id="user_prompt"
                    bind:value={userPrompt}
                    rows="4"
                    placeholder="例：この商品を、高級感のある大理石のテーブルの上に置いてください"
                    class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-violet-500 focus:border-violet-500"
                    disabled={isLoading}
                ></textarea>
            </div>

            <button
                id="submit"
                onclick={handleClick}
                disabled={isLoading || !selectedFile}
                class="w-full bg-violet-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
            >
                {#if isLoading}
                    <svg
                        class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            class="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            stroke-width="4"
                        ></circle>
                        <path
                            class="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                    </svg>
                    生成中...
                {:else}
                    画像生成を実行
                {/if}
            </button>
        </div>

        <!-- 右側：結果表示エリア -->
        <div
            class="p-4 border rounded-lg bg-gray-50 flex items-center justify-center min-h-[300px]"
        >
            {#if isLoading}
                <p class="text-gray-500">
                    AIが画像を生成中です。しばらくお待ちください...
                </p>
            {:else if errorMessage}
                <div class="text-red-600 bg-red-100 p-4 rounded-lg">
                    <h3 class="font-bold">エラーが発生しました</h3>
                    <p>{errorMessage}</p>
                </div>
            {:else if generatedImageUrl}
                <div>
                    <h3 class="font-semibold text-gray-700 mb-2 text-lg">
                        生成された画像
                    </h3>
                    <img
                        src={generatedImageUrl}
                        alt="Generated"
                        class="max-w-full h-auto rounded-md shadow-lg"
                    />
                </div>
            {:else}
                <p class="text-gray-500">
                    ここに生成された画像が表示されます。
                </p>
            {/if}
        </div>
    </div>
</main>
