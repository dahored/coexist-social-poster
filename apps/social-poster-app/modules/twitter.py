import tweepy
import os
from .json_utils import JSONHandler
from .file_utils import FileHandler
from dotenv import load_dotenv

class TwitterAPI:
    def __init__(self):
        """Carga credenciales desde .env e inicializa la API"""
        load_dotenv()
        consumer_key = os.getenv("X_CONSUMER_KEY")
        consumer_secret = os.getenv("X_CONSUMER_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        self.client = tweepy.Client(
            consumer_key=consumer_key, 
            consumer_secret=consumer_secret,
            access_token=access_token, 
            access_token_secret=access_token_secret
        )

        self.auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
        self.api = tweepy.API(self.auth)
        
        self.json_handler = JSONHandler(os.getenv("X_JSON_FILE"))
        self.file_handler = FileHandler()

    def upload_media(self, media_path):
        """Sube una imagen y devuelve su ID"""
        media = self.api.media_upload(media_path)
        return media.media_id

    def post_tweet(self, message, media_path=None, in_reply_to_tweet_id=None):
        """Publica un solo tweet con o sin imagen"""
        media_id = self.upload_media(media_path) if media_path else None
        return self.client.create_tweet(
            text=message, 
            media_ids=[media_id] if media_id else None, 
            in_reply_to_tweet_id=in_reply_to_tweet_id
        )

    def post_thread(self, tweets):
        """Publica un hilo de tweets con imágenes opcionales"""
        if not tweets:
            print("El hilo está vacío.")
            return
        
        first_text, first_media = tweets[0]
        first_tweet = self.post_tweet(first_text, first_media)
        tweet_id = first_tweet.data["id"]

        for text, media in tweets[1:]:
            response = self.post_tweet(text, media, in_reply_to_tweet_id=tweet_id)
            tweet_id = response.data["id"]
        
        print("Hilo publicado correctamente.")
        
    async def update_status_to_post_json(self, post_id):
        """Actualiza el estado de un tweet a 'posted' en el JSON"""
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["status"] = "posted"
                break  # Terminar la búsqueda después de encontrar el tweet

        await self.json_handler.save_json(data)  # Guardar cambios en el archivo JSON
        
    async def update_media_path_in_json(self, post_id, media_path):
        """Actualiza el campo media_path de un tweet en el JSON"""
        data = await self.json_handler.load_json()
        if not data:
            return

        for post in data["posts"]:
            if post["id"] == post_id:
                post["media_path"] = media_path
                break  # Detener la búsqueda después de actualizar el tweet

        await self.json_handler.save_json(data)  # Guardar los cambios en el JSON

    async def save_tweet_data_to_json(self, tweet_data):
        """Guarda los datos del tweet en la lista de 'posts' dentro del JSON de manera asíncrona."""
        if not tweet_data:
            return
        
        # Cargar el JSON actual
        json_data = await self.json_handler.load_json()

        # Asegurar que la clave 'posts' existe
        if "posts" not in json_data:
            json_data["posts"] = []

        # Buscar si el tweet ya existe en la lista de 'posts' y actualizarlo
        for i, existing_tweet in enumerate(json_data["posts"]):
            if existing_tweet["id"] == tweet_data["id"]:
                json_data["posts"][i] = tweet_data  # Actualizar tweet
                break
        else:
            json_data["posts"].append(tweet_data)  # Si no existe, agregarlo
        
        # Guardar el JSON actualizado
        await self.json_handler.save_json(json_data)


        
    async def get_tweet_to_post(self):
        """Obtiene el primer tweet con status 'not_posted'"""
        data = await self.json_handler.load_json()
        if not data:
            return None

        for post in data["posts"]:
            if post["status"] == "not_posted":
                return {
                    "id": post["id"],
                    "content": post["content"],
                    "prompt_to_media": post.get("prompt_to_media"),
                    "media_path": post["media_path"],
                    "hashtags": post["hashtags"],
                    "status": post["status"],
                    "is_thread": post["is_thread"],
                    "threads": post["threads"],
                }

        return None  # Si no hay tweets pendientes
    
    def get_thread_list(self, threads):
        """Obtiene la lista de tweets de un hilo"""
        thread_list = []
        for thread in threads:
            thread_list.append((thread["content"], thread["media_path"]))
        return thread_list
    
    async def preprocess_tweet_data(self, tweet_data):
        """Preprocesa los datos del tweet y sus threads."""
        if not tweet_data:
            return None

        # Función para procesar un solo tweet/thread
        async def process_single_tweet(data, base_id=None, thread_index=None):
            """Procesa un tweet o thread individual."""
            if len(data["content"]) > 280:
                print(f"El tweet con ID {data.get('id', 'desconocido')} excede el límite de 280 caracteres.")
                return None

            # Asignar ID para los threads (ejemplo: 400001, 400002, etc.)
            if base_id is not None and thread_index is not None:
                data["id"] = base_id * 100000 + (thread_index + 1)

            # Procesar imagen si es necesario
            media_path = data.get("media_path")
            if media_path:
                data["media_path"] = self.file_handler.get_media_path(media_path)
            elif data.get("prompt_to_media"):
                file_data = await self.file_handler.generate_media_by_prompt(data["prompt_to_media"], data["id"])
                if file_data:
                    data["media_path"] = file_data.get("full_path")
                    await self.update_media_path_in_json(data["id"], file_data.get("relative_path"))

            return data

        # Procesar el tweet principal
        tweet_data = await process_single_tweet(tweet_data)
        
        if tweet_data is None:
            return None

        # Procesar threads si existen
        if "threads" in tweet_data:
            base_id = tweet_data["id"]  # ID base del tweet principal
            processed_threads = []

            for index, thread in enumerate(tweet_data["threads"]):
                processed_thread = await process_single_tweet(thread, base_id, index)
                if processed_thread:
                    processed_threads.append(processed_thread)

            tweet_data["threads"] = processed_threads

        return tweet_data


    async def run_posts(self):
        print("Publicando en Twitter...")

        tweet_data = await self.get_tweet_to_post()  # Espera el resultado
        tweet_data = await self.preprocess_tweet_data(tweet_data)  # Ahora lo procesa
        await self.save_tweet_data_to_json(tweet_data)
        print(tweet_data)

        if not tweet_data:
            print("No hay tweets para publicar.")
            return

        # Obtener datos del tweet
        tweet_text = tweet_data.get("content")
        media_path = tweet_data.get("media_path")
        is_thread = tweet_data.get("is_thread")
        threads = tweet_data.get("threads")

        if is_thread:
            print("Publicando un hilo...")
            first_tweet = (tweet_text, media_path)
            thread_list = self.get_thread_list(threads)
            threads_tweet = [first_tweet] + thread_list
            # await self.post_thread(threads_tweet)  # Usa await si haces async post_thread()
        else:
            print("Publicando un tweet normal...")
            # await self.post_tweet(tweet_text, media_path)

        # await self.update_status_to_post_json(tweet_data["id"])

        print("Publicaciones en Twitter completadas.")

