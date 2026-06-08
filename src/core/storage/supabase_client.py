from dotenv import dotenv_values
from supabase import create_client, Client

from tool.path import PathConfig
from tool.debug import dbg


class SupabaseManager:
    _client: Client | None = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is not None:
            return cls._client

        env_dict = dotenv_values(dotenv_path=PathConfig.GEMINI_KEY)

        supabase_url = env_dict.get("SUPABASE_URL")
        supabase_key = env_dict.get("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            dbg.error("❌ 找不到 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY，請檢查 key.env")
            raise ValueError("Missing Supabase config")

        cls._client = create_client(supabase_url, supabase_key)
        dbg.log("✅ Supabase 連線初始化成功")
        return cls._client