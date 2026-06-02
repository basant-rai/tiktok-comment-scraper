import asyncio
import logging
import os
from flask import Flask, render_template, request, jsonify, send_file
from scraper import TikTokCommentScraper
from exporter import DataExporter
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.update(Config.__dict__)

os.makedirs(Config.LOGS_DIR, exist_ok=True)
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{Config.LOGS_DIR}/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

exporter = DataExporter(Config.OUTPUT_DIR)
scraper = TikTokCommentScraper(headless=True)

scraping_status = {
    "is_running": False,
    "progress": 0,
    "total": 0,
    "current_url": None,
    "error": None
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    try:
        data = request.get_json()
        video_url = data.get("video_url", "").strip()
        max_comments = int(data.get("max_comments", 200))
        export_format = data.get("export_format", "json")

        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400

        if not scraper.validate_url(video_url):
            return jsonify({"error": "Invalid TikTok URL format"}), 400

        if max_comments < 1 or max_comments > 10000:
            return jsonify({"error": "Max comments must be between 1 and 10000"}), 400

        if export_format not in Config.EXPORT_FORMATS:
            return jsonify({"error": f"Export format must be one of {Config.EXPORT_FORMATS}"}), 400

        scraping_status["is_running"] = True
        scraping_status["current_url"] = video_url
        scraping_status["error"] = None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            comments, metadata = loop.run_until_complete(
                scraper.scrape_comments(video_url, max_comments)
            )

            if export_format == "json":
                export_path = exporter.to_json(comments)
            elif export_format == "csv":
                export_path = exporter.to_csv(comments)
            elif export_format == "excel":
                export_path = exporter.to_excel(comments)

            summary = exporter.get_export_summary(comments)

            scraping_status["is_running"] = False

            return jsonify({
                "success": True,
                "metadata": metadata,
                "summary": summary,
                "export_file": os.path.basename(export_path),
                "total_comments": len(comments),
            }), 200

        except Exception as e:
            scraping_status["is_running"] = False
            scraping_status["error"] = str(e)
            logger.error(f"Scraping error: {e}")
            return jsonify({"error": str(e)}), 500

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(scraping_status), 200


@app.route("/api/download/<filename>", methods=["GET"])
def api_download(filename):
    try:
        filepath = os.path.join(Config.OUTPUT_DIR, filename)

        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/exports", methods=["GET"])
def api_list_exports():
    try:
        files = []
        if os.path.exists(Config.OUTPUT_DIR):
            for filename in sorted(os.listdir(Config.OUTPUT_DIR), reverse=True):
                filepath = os.path.join(Config.OUTPUT_DIR, filename)
                if os.path.isfile(filepath):
                    files.append({
                        "name": filename,
                        "size": os.path.getsize(filepath),
                        "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    })
        return jsonify({"files": files}), 200
    except Exception as e:
        logger.error(f"Export list error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/validate-url", methods=["POST"])
def api_validate_url():
    try:
        data = request.get_json()
        url = data.get("url", "").strip()

        is_valid = scraper.validate_url(url)
        video_id = scraper.extract_video_id(url) if is_valid else None

        return jsonify({
            "valid": is_valid,
            "video_id": video_id,
            "message": "Valid TikTok URL" if is_valid else "Invalid TikTok URL format"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting TikTok Comment Scraper")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
