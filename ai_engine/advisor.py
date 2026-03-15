"""
File: ai_engine/advisor.py
Purpose: Send cluster summaries to Ollama and get actionable recommendations
"""

import requests
import pandas as pd
from utils.logger import setup_logger
from utils.file_utils import ensure_dir, save_json


CLUSTER_NAMES = {0: 'Frequent low spenders', 1: 'VIP', 2: 'At risk', 3: 'Middle tier'}

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:latest"


class CustomerAdvisor:

    def __init__(self, model: str = MODEL_NAME):
        self.model = model
        self.logger = setup_logger("advisor")
        ensure_dir("outputs/advice")

    def _build_prompt(self, cluster_id: int, stats: dict) -> str:
        """بني الـ prompt اللي هيتبعت لـ Ollama"""
        return f"""
You are a customer success and marketing strategy expert.

I have a customer segment with the following characteristics:
- Segment name: {CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}')}
- Number of customers: {stats['count']}
- Average total spent: ${stats['avg_spent']:,.2f}
- Average number of purchases: {stats['avg_purchases']:.1f}
- Average purchase amount: ${stats['avg_order_value']:,.2f}

Based on these numbers, provide:
1. A one-line description of this customer type
2. Three specific marketing or retention strategies for this segment
3. One risk to watch out for

Be concise and practical. Use bullet points.
""".strip()

    def _call_ollama(self, prompt: str) -> str:
        """ابعت الـ prompt لـ Ollama وارجع الرد"""
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=180
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.ConnectionError:
            self.logger.error("Ollama is not running — start it with: ollama serve")
            return None
        except requests.exceptions.Timeout:
            self.logger.error("Ollama request timed out")
            return None
        except Exception as e:
            self.logger.error(f"Ollama error: {e}")
            return None

    def _get_cluster_stats(self, df: pd.DataFrame, cluster_id: int) -> dict:
        """احسب إحصائيات الـ cluster"""
        group = df[df['cluster'] == cluster_id]
        avg_purchases = group['total_purchases'].mean()
        avg_spent = group['total_spent'].mean()

        return {
            'count': int(len(group)),
            'avg_spent': float(avg_spent),
            'avg_purchases': float(avg_purchases),
            'avg_order_value': float(avg_spent / max(avg_purchases, 1))
        }

    def advise(self, df: pd.DataFrame) -> dict:
        """
        شغّل الـ advisor على كل cluster وارجع النصايح

        Args:
            df: clustered DataFrame (لازم يكون فيه عمود 'cluster')

        Returns:
            dict: cluster_id -> advice text
        """
        if 'cluster' not in df.columns:
            self.logger.error("DataFrame has no 'cluster' column — run trainer first")
            return {}

        results = {}
        cluster_ids = sorted(df['cluster'].unique())

        self.logger.info(f"Getting advice for {len(cluster_ids)} clusters...")

        for cluster_id in cluster_ids:
            name = CLUSTER_NAMES.get(cluster_id, f'Cluster {cluster_id}')
            self.logger.info(f"Asking Ollama about: {name}...")

            stats = self._get_cluster_stats(df, cluster_id)
            prompt = self._build_prompt(cluster_id, stats)
            advice = self._call_ollama(prompt)

            if advice:
                results[int(cluster_id)] = {
                    'cluster_name': name,
                    'stats': stats,
                    'advice': advice
                }
                self.logger.info(f"Got advice for {name}")
            else:
                self.logger.warning(f"No advice received for {name}")

        # احفظ النتايج
        if results:
            self._save_results(results)

        return results

    def _save_results(self, results: dict):
        """احفظ النصايح كـ JSON وكـ text مقروء"""
        # JSON
        save_json(results, "outputs/advice/advice.json")

        # Text file مقروء
        txt_path = "outputs/advice/advice.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("CUSTOMER SEGMENT ADVISORY REPORT\n")
            f.write("=" * 60 + "\n\n")

            for cluster_id, data in results.items():
                f.write(f"SEGMENT: {data['cluster_name'].upper()}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Customers : {data['stats']['count']}\n")
                f.write(f"Avg spent : ${data['stats']['avg_spent']:,.2f}\n")
                f.write(f"Avg orders: {data['stats']['avg_purchases']:.1f}\n")
                f.write(f"Avg order : ${data['stats']['avg_order_value']:,.2f}\n\n")
                f.write("Advice:\n")
                f.write(data['advice'])
                f.write("\n\n" + "=" * 60 + "\n\n")

        self.logger.info("Advice saved to: outputs/advice/")