import logging
import os
import json
from dotenv import load_dotenv

from livekit import agents, api
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (

    cartesia,
    deepgram,
    noise_cancellation,
    silero,
    groq,
)
from livekit.agents import llm
from typing import Annotated, Optional

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outbound-agent")


# TRUNK ID - This needs to be set after you crate your trunk
# You can find this by running 'python setup_trunk.py --list' or checking LiveKit Dashboard
OUTBOUND_TRUNK_ID = os.getenv("OUTBOUND_TRUNK_ID")
SIP_DOMAIN = os.getenv("VOBIZ_SIP_DOMAIN") 


def _build_tts():
    """Configure the Text-to-Speech provider based on env vars."""
    provider = os.getenv("TTS_PROVIDER", "openai").lower()
    
    if provider == "cartesia":
        logger.info("Using Cartesia TTS")
        model = os.getenv("CARTESIA_TTS_MODEL", "sonic-2")
        voice = os.getenv("CARTESIA_TTS_VOICE", "f786b574-daa5-4673-aa0c-cbe3e8534c02")
        return cartesia.TTS(model=model, voice=voice)
    
    # Default to OpenAI
    logger.info("Using OpenAI TTS")
    model = os.getenv("OPENAI_TTS_MODEL", "tts-1")
    voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
    return openai.TTS(model=model, voice=voice)



class TransferFunctions(llm.ToolContext):
    def __init__(self, ctx: agents.JobContext, phone_number: str = None):
        super().__init__(tools=[])
        self.ctx = ctx
        self.phone_number = phone_number

    @llm.function_tool(description="Transfer the call to a human support agent or another phone number.")
    async def transfer_call(self, destination: Optional[str] = None):
        """
        Transfer the call.
        """
        if destination is None:
            destination = os.getenv("DEFAULT_TRANSFER_NUMBER")
            if not destination:
                 return "Error: No default transfer number configured."
        if "@" not in destination:
            # If no domain is provided, append the SIP domain
            if SIP_DOMAIN:
                # Ensure clean number (strip tel: or sip: prefix if present but no domain)
                clean_dest = destination.replace("tel:", "").replace("sip:", "")
                destination = f"sip:{clean_dest}@{SIP_DOMAIN}"
            else:
                # Fallback to tel URI if no domain configured
                if not destination.startswith("tel:") and not destination.startswith("sip:"):
                     destination = f"tel:{destination}"
        elif not destination.startswith("sip:"):
             destination = f"sip:{destination}"
        
        logger.info(f"Transferring call to {destination}")
        
        # Determine the participant identity
        # For outbound calls initiated by this agent, the participant identity is typically "sip_<phone_number>"
        # For inbound, we might need to find the remote participant.
        participant_identity = None
        
        # If we stored the phone number from metadata, we can construct the identity
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


class OutboundAssistant(Agent):

    """
    An AI agent tailored for outbound calls.
    Attempts to be helpful and concise.
    """
    def __init__(self) -> None:
        super().__init__(
            instructions="""
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
English: Hello! Thank you for calling Mansa InfoTech. This is Mohsum Rakhse, your virtual receptionist. How may I assist you with your technology or software requirements today?  
If outbound: Hello, this is Mohsum Rakhse calling from Mansa InfoTech. We provide AI agents, calling systems, chatbots, and more. May I know if you have any current technology needs I can assist with?

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
        )


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the agent.
    
    For outbound calls:
    1. Checks for 'phone_number' in the job metadata.
    2. Connects to the room.
    3. Initiates the SIP call to the phone number.
    4. Waits for answer before speaking.
    """
    logger.info(f"Connecting to room: {ctx.room.name}")
    
    # parse the phone number from the metadata sent by the dispatch script
    phone_number = None
    try:
        if ctx.job.metadata:
            data = json.loads(ctx.job.metadata)
            phone_number = data.get("phone_number")
    except Exception:
        logger.warning("No valid JSON metadata found. This might be an inbound call.")

    # Initialize function context
    fnc_ctx = TransferFunctions(ctx, phone_number)

    # Initialize the Agent Session with plugins

    session = AgentSession(
        # stt=deepgram.STT(model="nova-3", language="multi"),
        # llm=groq.LLM(),
        # tts=_build_tts(),
        # tools=fnc_ctx.all_tools,
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=groq.LLM(
            model="llama-3.1-8b-instant"
        ),
         tts = cartesia.TTS(
        model="sonic-3",
        voice="638efaaa-4d0c-442e-b701-3fae16aad012" 
        ),
        vad=silero.VAD.load(),
    )

    # Start the session
    await session.start(
        room=ctx.room,
        agent=OutboundAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVCTelephony(),
            close_on_disconnect=True, # Close room when agent disconnects
        ),
    )

    if phone_number:
        logger.info(f"Initiating outbound SIP call to {phone_number}...")
        try:
            # Create a SIP participant to dial out
            # This effectively "calls" the phone number and brings them into this room
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=OUTBOUND_TRUNK_ID,
                    sip_call_to=phone_number,
                    participant_identity=f"sip_{phone_number}", # Unique ID for the SIP user
                    wait_until_answered=True, # Important: Wait for pickup before continuing
                )
            )
            logger.info("Call answered! Agent is now listening.")
            
            # Note: We do NOT generate an initial reply here immediately.
            # Usually for outbound, we want to hear "Hello?" from the user first,
            # OR we can speak immediately. 
            # If you want the agent to speak first, uncomment the lines below:
            
            # await session.generate_reply(
            #     instructions="The user has answered. Introduce yourself immediately."
            # )
            
        except Exception as e:
            logger.error(f"Failed to place outbound call: {e}")
            # Ensure we clean up if the call fails
            ctx.shutdown()
    else:
        # Fallback for inbound calls (if this agent is used for that)
        logger.info("No phone number in metadata. Treating as inbound/web call.")
        await session.generate_reply(instructions="Greet the user.")


if __name__ == "__main__":
    # The agent name "outbound-caller" is used by the dispatch script to find this worker
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller", 
        )
    )
