import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.db import database_sync_to_async
from .models import Session
from .scoring import compute_score

class CoachConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close(code=4003)
            return

        self.should_save = False 
        self.session_state = {
            "frames": 0, "crossed_frames": 0, "movement_mean": 0.0,
            "movement_m2": 0.0, "eye_sum": 0.0, "sym_sum": 0.0, "jerk_sum": 0.0,
            "start_time": timezone.now()
        }

        self.last_problems = [] 
        self.last_sent_score = 0
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
    

        if data.get("type") == "end_session":
            self.should_save = True
            await self.finish_and_close()
            return
        
        if data.get("type") == "cancel_session":
            self.should_save = False
            await self.close()
            return

        
        st = self.session_state
        st["frames"] += 1
        current_problems = []
        

        if int(data.get("hands_crossed", 0)):
            current_problems.append("Розчепіть руки")
            st["crossed_frames"] += 1

        if float(data.get("eye_contact", 0)) < 0.5:
            current_problems.append("Дивіться в камеру")
            st["eye_sum"] += 0
        else:
            st["eye_sum"] += 1

        if float(data.get("symmetry", 0)) > 0.1:
            current_problems.append("Вирівняйте спину")
            st["sym_sum"] += float(data.get("symmetry", 0))


        n = st["frames"]
        score = round(((1 - (st["crossed_frames"] / n)) * 40 + (st["eye_sum"] / n) * 40 + 20), 1)

        problems_changed = set(current_problems) != set(self.last_problems)
        score_changed = abs(score - self.last_sent_score) > 10.0

        if problems_changed or score_changed:
            self.last_problems = current_problems
            self.last_sent_score = score
            await self.send(json.dumps({
                "type": "live_update",
                "score": score,
                "problems": current_problems
            }))

    async def finish_and_close(self):
        st = self.session_state
        n = st["frames"]
        if n > 10: 
            pc = st["crossed_frames"] / n
            m_bar = st["movement_mean"]
            sigma = (st["movement_m2"] / n)**0.5
            eye = st["eye_sum"] / n
            sym = st["sym_sum"] / n
            jerk = st["jerk_sum"] / n

            final_score = compute_score(pc, m_bar, sigma, eye, sym, jerk)
            await self.save_session(final_score, st["start_time"], timezone.now())
            await self.send(json.dumps({"type": "final_score", "score": final_score}))
        
        await self.close()

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def save_session(self, score, start, end):
        Session.objects.create(user=self.user, start_time=start, end_time=end, score=score)