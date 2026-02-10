import logging
import os
import json
import asyncio
from datetime import datetime
from typing import Annotated, Optional, List, Dict, Any

from dotenv import load_dotenv
import scipy.io.wavfile as wav
import numpy as np

from livekit import agents, api
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import (
    cartesia,
    deepgram,
    silero,
    groq,
)

# Only import noise cancellation if specifically needed to save memory
# from livekit.plugins import noise_cancellation

# Attempt to import openai if available
try:
    from livekit.plugins import openai
except ImportError:
    openai = None

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outbound-agent")


# --- Configuration ---
class Config:
    OUTBOUND_TRUNK_ID = os.getenv("OUTBOUND_TRUNK_ID")
    SIP_DOMAIN = os.getenv("VOBIZ_SIP_DOMAIN")
    DEFAULT_TRANSFER_NUMBER = os.getenv("DEFAULT_TRANSFER_NUMBER")
    
    # STT Configuration
    STT_PROVIDER = os.getenv("STT_PROVIDER", "deepgram").lower()
    STT_MODEL = os.getenv("STT_MODEL", "nova-3")
    STT_LANGUAGE = os.getenv("STT_LANGUAGE", "multi")

    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    
    # TTS Configuration
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "cartesia").lower()
    # Cartesia
    CARTESIA_MODEL = os.getenv("CARTESIA_TTS_MODEL", "sonic-3") # Updated default from code
    CARTESIA_VOICE = os.getenv("CARTESIA_TTS_VOICE", "f786b574-daa5-4673-aa0c-cbe3e8534c02") # Updated default
    # OpenAI
    OPENAI_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
    OPENAI_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")
    # Deepgram
    DEEPGRAM_TTS_MODEL = os.getenv("DEEPGRAM_TTS_MODEL", "aura-asteria-en")


# --- Instructions ---
AGENT_INSTRUCTIONS = """
SECTION 1: Demeanour & Identity

Personality  
mosuam Rakse is a professional, polite, and concise virtual receptionist and AI calling agent representing Mansa InfoTech Technology Services. He speaks clearly with a calm and courteous tone, ensuring every caller feels heard and supported. Mohsum never deviates from the technology focus of Mansa InfoTech services and maintains professionalism throughout the call. He adapts to the caller’s pace and responds precisely, avoiding unnecessary details or personal opinions. His manner is structured yet warm, guiding callers smoothly through the conversation.

Context  
Mohsum handles both inbound and outbound calls for Mansa InfoTech, a company offering specialized technology and software development services. He fields questions strictly related to AI agents, voice calling, chatbots, telephony integrations, LLM integrations, and related IT offerings. Callers may be business clients or individuals seeking custom technology solutions. Mohsum’s role is to understand their technical requirements, collect lead information, and if needed, schedule a consultation call with senior technical consultants.

Environment  
Calls take place via phone lines or VOIP, demanding short, clear sentences suitable for voice interaction. Mohsum’s tone remains professional and focused. He never indulges in off-topic conversations or jokes and politely declines non-technology-related queries, steering the conversation back to Mansa InfoTech’s service offerings.

Tone  
Mohsum’s voice is respectful, friendly, and efficient. He is patient and listens actively, asking smart, relevant questions to understand callers’ needs. He pauses appropriately to allow callers to respond and never interrupts. When the caller needs more detailed help, Mohsum offers to schedule a consultation politely without pressure.

Goal  
His main objectives are:  
- Greet callers and introduce Mansa InfoTech professionally  
- Understand technology-related requirements clearly (AI agents, chatbots, telephony, LLMs, etc.)  
- Collect mandatory lead details: full name, email address, and contact number  
- Offer to book a detailed consultation call with senior consultants if appropriate  
- Politely refuse unrelated or off-topic queries without providing irrelevant information  
- End calls warmly, leaving a positive impression about Mansa InfoTech

Guardrails  
- Only provide information about Mansa InfoTech’s specified technology and software services  
- Do not answer non-technology or unrelated questions; politely decline and redirect  
- Avoid personal opinions, jokes, or casual banter  
- Never provide information beyond the scope of Mansa InfoTech’s offerings  
- Keep communication clear, concise, and professional at all times

Interview Structure & Flow

Call Opening (Inbound & Outbound):  
English: Hello! Thank you for calling Mansa InfoTech. This is Mousam Rakse, your virtual receptionist. How may I assist you with your technology or software requirements today?  
If outbound: Hello, this is Mousam Rakse calling from Mansa InfoTech. We provide AI agents, calling systems, chatbots, and more. May I know if you have any current technology needs I can assist with?

Lead Collection:  
English: May I please have your full name?  
English: Could you share your email address so our technical team can contact you?  
English: May I have your contact number for further communication?

Requirement Discovery:  
English: What type of solution are you looking for? (AI agent, calling system, chatbot, app, website, automation, etc.)  
English: Is this for a business or personal project?  
English: Do you need integration with phone numbers, CRM, or LiveKit?  
English: Are you using any LLM like Gemini, OpenAI, Grok, or others?

Booking Consultation:  
If caller needs detailed assistance or project discussion:  
English: Would you like me to arrange a consultation call with our senior technical consultant?  
If yes: English: Thank you! I will forward your details to our senior consultant team. They will contact you shortly to discuss your requirements in detail.

Non-Tech Query Handling:  
If the caller asks anything unrelated to technology or Mansa InfoTech services:  
English: I’m here to assist only with technology and Mansa InfoTech services. Could you please share your technical requirement?

End Call Message:  
English: Thank you for contacting Mansa InfoTech. Your request has been noted. Our team will connect with you shortly. Have a great day!

Language and Style  
English language only  
Use short, professional, and courteous sentences suitable for voice communications  
Avoid repetition, filler words, or off-topic details  
Always maintain polite tone even when declining non-pertinent queries

SECTION 2: INTERVIEW STARTER  

Inbound/Outbound Call Opening:  
English: Hello! Thank you for calling Mansa InfoTech. This is Mohsum Rakhse, your virtual receptionist. How may I assist you with your technology or software requirements today?  
Outbound call option: Hello, this is Mohsum Rakhse calling from Mansa InfoTech. We provide AI agents, calling systems, chatbots, and more. May I know if you have any current technology needs I can assist with?

SECTION 3: LEAD COLLECTION  

English: May I please have your full name?  
English: Could you share your email address so our technical team can contact you?  
English: May I have your contact number for further communication?

SECTION 4: UNDERSTANDING REQUIREMENT  

English: What type of solution are you looking for? (AI agent, calling system, chatbot, app, website, automation, etc.)  
English: Is this for a business or personal project?  
English: Do you need integration with phone numbers, CRM, or LiveKit?  
English: Are you using any LLM like Gemini, OpenAI, Grok, or others?

SECTION 5: BOOKING CONSULTATION  

English: Would you like me to arrange a consultation call with our senior technical consultant?  
If yes: English: Thank you! I will forward your details to our senior consultant team. They will contact you shortly to discuss your requirements in detail.

SECTION 6: NON-TECH QUERY HANDLING  

English: I’m here to assist only with technology and Mansa InfoTech services. Could you please share your technical requirement?

SECTION 7: END CALL MESSAGE  

English: Thank you for contacting Mansa InfoTech. Your request has been noted. Our team will connect with you shortly. Have a great day!
"""


# --- Model Builders ---
def _build_stt():
    if Config.STT_PROVIDER == "deepgram":
        logger.info(f"Using Deepgram STT (Model: {Config.STT_MODEL})")
        return deepgram.STT(model=Config.STT_MODEL, language=Config.STT_LANGUAGE)
    # Add other providers here if needed
    logger.warning(f"Unknown STT provider '{Config.STT_PROVIDER}', defaulting to Deepgram.")
    return deepgram.STT(model=Config.STT_MODEL, language=Config.STT_LANGUAGE)


def _build_llm():
    if Config.LLM_PROVIDER == "groq":
        logger.info(f"Using Groq LLM (Model: {Config.LLM_MODEL})")
        return groq.LLM(model=Config.LLM_MODEL)
    # Add other providers here
    logger.warning(f"Unknown LLM provider '{Config.LLM_PROVIDER}', defaulting to Groq.")
    return groq.LLM(model=Config.LLM_MODEL)


def _build_tts():
    """Configure the Text-to-Speech provider based on env vars."""
    if Config.TTS_PROVIDER == "cartesia":
        logger.info(f"Using Cartesia TTS (Model: {Config.CARTESIA_MODEL})")
        return cartesia.TTS(model=Config.CARTESIA_MODEL, voice=Config.CARTESIA_VOICE)
    
    if Config.TTS_PROVIDER == "openai":
        if openai:
            logger.info(f"Using OpenAI TTS (Model: {Config.OPENAI_MODEL})")
            return openai.TTS(model=Config.OPENAI_MODEL, voice=Config.OPENAI_VOICE)
        else:
            logger.error("OpenAI TTS requested but livekit-plugins-openai not installed.")
            raise ImportError("livekit-plugins-openai not installed/imported")

    if Config.TTS_PROVIDER == "deepgram":
        logger.info(f"Using Deepgram TTS (Model: {Config.DEEPGRAM_TTS_MODEL})")
        return deepgram.TTS(model=Config.DEEPGRAM_TTS_MODEL)
            
    # Fallback to Cartesia if unknown
    logger.warning(f"Unknown TTS provider '{Config.TTS_PROVIDER}', defaulting to Cartesia.")
    return cartesia.TTS(model=Config.CARTESIA_MODEL, voice=Config.CARTESIA_VOICE)


# --- Tools ---
class TransferFunctions(llm.ToolContext):
    def __init__(self, ctx: agents.JobContext, phone_number: str = None):
        super().__init__(tools=[])
        self.ctx = ctx
        self.phone_number = phone_number

    @llm.function_tool(description="Transfer the call to a human support agent or another phone number.")
    async def transfer_call(self, destination: Optional[str] = None):
        """
        Transfer the call to a human or another number.
        """
        if destination is None:
            destination = Config.DEFAULT_TRANSFER_NUMBER
            if not destination:
                 return "Error: No default transfer number configured."

        # Handle SIP/TEL URI formatting
        if "@" not in destination:
            if Config.SIP_DOMAIN:
                # Ensure clean number
                clean_dest = destination.replace("tel:", "").replace("sip:", "")
                destination = f"sip:{clean_dest}@{Config.SIP_DOMAIN}"
            else:
                # Fallback to tel URI
                if not destination.startswith("tel:") and not destination.startswith("sip:"):
                     destination = f"tel:{destination}"
        elif not destination.startswith("sip:"):
             destination = f"sip:{destination}"
        
        logger.info(f"Transferring call to {destination}")
        
        # Determine the participant identity
        participant_identity = None
        if self.phone_number:
            participant_identity = f"sip_{self.phone_number}"
        else:
            # Try to find a participant that is NOT the agent
            for p in self.ctx.room.remote_participants.values():
                participant_identity = p.identity
                break
        
        if not participant_identity:
            logger.error("Could not determine participant identity for transfer")
            return "Failed to transfer: could not identify the caller."

        try:
            logger.info(f"Transferring participant {participant_identity} to {destination}")
            await self.ctx.api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=self.ctx.room.name,
                    participant_identity=participant_identity,
                    transfer_to=destination,
                    play_dialtone=False
                )
            )
            return "Transfer initiated successfully."
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return f"Error executing transfer: {e}"


# --- Helpers ---
class TranscriptManager:
    @staticmethod
    async def save_transcript(ctx: agents.JobContext, session: AgentSession, phone_number: str):
        """Saves transcript in both JSON and TXT format."""
        try:
            if not hasattr(session, "chat_context"):
                logger.warning("Session has no chat_context, skipping transcript save.")
                return

            messages = session.chat_context.messages
            conversation_log = []
            json_log = []

            for msg in messages:
                role = msg.role
                content = ""
                
                if isinstance(msg.content, list):
                    content = " ".join([str(c) for c in msg.content])
                elif isinstance(msg.content, str):
                    content = msg.content

                if not content or not content.strip():
                    continue

                role_map = {"assistant": "Agent", "user": "User", "system": "System"}
                display_role = role_map.get(role, role.capitalize())
                
                # Text log entry
                conversation_log.append(f"{display_role}: {content}")
                
                # JSON log entry
                json_log.append({
                    "role": role,
                    "display_role": display_role,
                    "content": content,
                    "timestamp": datetime.now().isoformat() # Ideally capture real message timestamp if available
                })

            safe_job_id = "".join([c for c in ctx.job.id if c.isalnum() or c in ("-", "_")])
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # --- Save TXT ---
            txt_dir = "transcripts"
            os.makedirs(txt_dir, exist_ok=True)
            txt_filename = f"{txt_dir}/call_{safe_job_id}.txt"
            
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write("Call Transcript\n")
                f.write(f"Job ID: {ctx.job.id}\n")
                f.write(f"Phone: {phone_number if phone_number else 'Unknown'}\n")
                f.write(f"Timestamp: {timestamp_str}\n\n")
                for line in conversation_log:
                    f.write(f"{line}\n")
            
            logger.info(f"Saved text transcript to {txt_filename}")

            # --- Save JSON ---
            json_dir = "transcripts_json"
            os.makedirs(json_dir, exist_ok=True)
            json_filename = f"{json_dir}/call_{safe_job_id}.json"
            
            meta_data = {
                "job_id": ctx.job.id,
                "phone_number": phone_number,
                "timestamp": timestamp_str,
                "messages": json_log
            }
            
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2)
                
            logger.info(f"Saved JSON transcript to {json_filename}")

        except Exception as e:
            logger.error(f"Failed to save transcripts: {e}")


class AudioRecorder:
    def __init__(self, room: api.Room, job_id: str):
        self.room = room
        self.job_id = job_id
        self.audio_frames = []
        self.sample_rate = 48000
        self.recording = True
        self.task = None

    async def start(self):
        self.task = asyncio.create_task(self._record_loop())

    async def _record_loop(self):
        # Setup listener
        @self.room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            if track.kind == "audio":
                logger.info(f"Subscribed to user audio: {participant.identity}")
                asyncio.create_task(self._capture_audio(track))

    async def _capture_audio(self, track):
        stream = api.AudioStream(track)
        async for event in stream:
            if not self.recording: break
            # event.frame is an AudioFrame
            data = np.frombuffer(event.frame.data, dtype=np.int16)
            self.audio_frames.append(data)
            self.sample_rate = event.frame.sample_rate

    async def stop_and_save(self):
        self.recording = False
        if self.task:
            self.task.cancel() # Or modify loop to check flag
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        if self.audio_frames:
            logger.info("Saving user audio recording...")
            try:
                full_audio = np.concatenate(self.audio_frames)
                os.makedirs("recordings_audio", exist_ok=True)
                filename = f"recordings_audio/user_{self.job_id}_{int(datetime.now().timestamp())}.wav"
                wav.write(filename, self.sample_rate, full_audio)
                logger.info(f"✅ Saved user audio to: {filename}")
            except Exception as e:
                logger.error(f"Failed to write wav file: {e}")
        else:
            logger.warning("No audio frames captured from user.")


# --- Main Agent ---
class OutboundAssistant(Agent):
    """
    An AI agent tailored for outbound calls.
    """
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTIONS)


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the agent.
    """
    logger.info(f"Connecting to room: {ctx.room.name}")
    
    # Parse metadata
    phone_number = None
    try:
        if ctx.job.metadata:
            data = json.loads(ctx.job.metadata)
            phone_number = data.get("phone_number")
    except Exception:
        logger.warning("No valid JSON metadata found. This might be an inbound call.")

    # Initialize function context with tools
    fnc_ctx = TransferFunctions(ctx, phone_number)

    # Initialize Session
    session = AgentSession(
        stt=_build_stt(),
        llm=_build_llm(),
        tts=_build_tts(),
        vad=silero.VAD.load(),
    )

    disconnect_event = asyncio.Event()
    
    # Handle Shutdown/Disconnect
    ctx.add_shutdown_callback(lambda: disconnect_event.set())
    
    # Transcript saving flag
    has_saved = False
    
    async def save_once():
        nonlocal has_saved
        if not has_saved:
            has_saved = True
            logger.info("Executing transcript save...")
            await TranscriptManager.save_transcript(ctx, session, phone_number)

    @ctx.room.on("disconnected")
    def on_disconnected(reason=None):
        logger.info(f"Room disconnected (reason: {reason}). Saving transcript...")
        asyncio.create_task(save_once())
        disconnect_event.set()

    # Audio Recording
    recorder = AudioRecorder(ctx.room, ctx.job.id)
    await recorder.start()

    # Start Session
    await session.start(
        room=ctx.room,
        agent=OutboundAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVCTelephony(),
            close_on_disconnect=True,
        ),
    )

    # Handle Outbound Logic
    if phone_number:
        logger.info(f"Initiating outbound SIP call to {phone_number}...")
        try:
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=Config.OUTBOUND_TRUNK_ID,
                    sip_call_to=phone_number,
                    participant_identity=f"sip_{phone_number}", 
                    wait_until_answered=True, 
                )
            )
            logger.info("Call answered! Agent is now listening.")
        except Exception as e:
            logger.error(f"Failed to place outbound call: {e}")
            ctx.shutdown()
    else:
        logger.info("No phone number in metadata. Treating as inbound/web call.")
        await session.generate_reply(instructions="Greet the user.")

    # Wait for completion
    logger.info("Session started. Waiting for disconnect...")
    try:
        await disconnect_event.wait()
    except asyncio.CancelledError:
        logger.info("Session cancelled.")
    finally:
        logger.info("Session ending process...")
        await recorder.stop_and_save()
        await save_once()
        logger.info("Session cleanup complete.")


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="transcription-agent", 
        )
    )
