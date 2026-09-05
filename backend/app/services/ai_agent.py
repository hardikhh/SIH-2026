import json
import os
import re
from typing import Dict, Any, List, Tuple
from app.config import settings
from app.schemas.beneficiary import BeneficiaryProfileExtract

# Multilingual question prompts and quick replies
DIALOGUE_SCRIPTS = {
    "hi": {
        "welcome": "नमस्ते! मैं आपका पीएम-अजय आजीविका एवं कौशल साथी हूँ। सबसे पहले बताएं आप किस राज्य, जिले या गाँव/पिनकोड में रहते हैं (जैसे गुजरात या राजस्थान)? और आपने कहाँ तक पढ़ाई की है?",
        "ask_education": "आपकी पढ़ाई कहाँ तक हुई है? जैसे 8वीं, 10वीं पास या कोई फॉर्मल पढ़ाई नहीं?",
        "ask_skills": "आपने पहले क्या काम किया है या आपको कौन-कौन से औजार या काम चलाना आता है? जैसे बिजली, सिलाई, खेती, वाहन आदि?",
        "ask_interests": "आप भविष्य में किस तरह का नया काम सीखना चाहते हैं? किस काम में आपका मन लगता है?",
        "ask_mobility": "आप काम या ट्रेनिंग के लिए गाँव से कितनी दूर (किलोमीटर) तक जा सकते हैं? क्या आपको चलने-फिरने में कोई दिक्कत है?",
        "ask_preference": "आप किसी कंपनी में मासिक वेतन पर नौकरी करना चाहते हैं, या पीएम-अजय अनुदान से अपनी दुकान/स्वरोजगार शुरू करना चाहते हैं?",
        "ask_location": "आप किस राज्य, जिले या गाँव/पिनकोड में रहते हैं? अपना पूरा पता या जिला बताएं (जैसे — गुजरात के अहमदाबाद/सूरत या राजस्थान के जयपुर/जोधपुर) ताकि हम आपके सबसे पास का केंद्र खोज सकें।",
        "complete": "बहुत बढ़िया! आपकी जानकारी दर्ज हो गई है। अब हम आपके पते व जिले के आधार पर सबसे उपयुक्त 3 सरकारी NSQF प्रशिक्षण एवं आजीविका विकल्प दिखा रहे हैं।",
        "quick_replies": {
            "education": ["8वीं पास", "10वीं पास", "12वीं पास", "स्कूल नहीं गए"],
            "skills": ["बिजली का काम", "सिलाई-कढ़ाई", "खेती-बाड़ी", "मोटरसाइकिल रिपेयर", "प्लंबर/नलसाजी"],
            "interests": ["सोलर एनर्जी", "मोबाइल रिपेयरिंग", "डेयरी व दूध", "कपड़ा सिलाई", "हॉस्पिटैलिटी"],
            "preference": ["मासिक नौकरी (Salary)", "अपनी दुकान/स्वरोजगार (Self-employed)", "दोनों चलेगा"],
            "location_gj": ["अहमदाबाद", "सूरत", "वडोदरा", "राजकोट", "मेहसाणा", "कच्छ", "भावनगर", "आनंद", "गांधीनगर", "जामनगर", "जूनागढ़", "दाहोद", "बनासकांठा", "भरूच", "मोरबी", "नवसारी", "वलसाड"],
            "location_rj": ["जयपुर", "जोधपुर", "कोटा", "उदयपुर", "बीकानेर", "अजमेर", "अलवर", "भीलवाड़ा", "सीकर", "भरतपुर", "पाली", "बाड़मेर", "नागौर", "चित्तौड़गढ़", "झुंझुनू", "श्रीगंगानगर"]
        }
    },
    "gu": {
        "welcome": "નમસ્તે! હું તમારો પીએમ-અજય આજીવિકા અને કૌશલ્ય સહાયક છું. સૌથી પહેલા જણાવો કે તમે કયા રાજ્ય, જિલ્લા કે ગામ/પિનકોડમાં રહો છો (જેમ કે ગુજરાત કે રાજસ્થાન)? અને તમે કેટલો અભ્યાસ કર્યો છે?",
        "ask_education": "તમે ક્યાં સુધી અભ્યાસ કર્યો છે? જેમ કે 8 પાસ, 10 પાસ કે કોઈ ઔપચારિક શિક્ષણ નથી?",
        "ask_skills": "તમે અગાઉ કયું કામ કર્યું છે અથવા તમને કયા ઓજારો કે સાધનો ચલાવતા આવડે છે? જેમ કે વાયરિંગ, દરજીકામ, ખેતી વગેરે?",
        "ask_interests": "તમે ભવિષ્યમાં કયું નવું કામ શીખવા માંગો છો? તમને કયા ક્ષેત્રમાં રસ છે?",
        "ask_mobility": "તમે તાલીમ કે કામ માટે તમારા ગામ/વિસ્તારથી કેટલા કિલોમીટર દૂર જઈ શકો છો? ચાલવા-ફરવામાં કોઈ તકલીફ છે?",
        "ask_preference": "તમારે કંપનીમાં પગારવાળી નોકરી કરવી છે, કે પીએમ-અજય ગ્રાન્ટથી પોતાની દુકાન/સ્વરોજગાર શરૂ કરવો છે?",
        "ask_location": "તમે ક્યા રાજ્ય, જિલ્લા કે ગામ/પિનકોડમાં રહો છો? તમારું પૂરું સરનામું અથવા જિલ્લો જણાવો (દા.ત. — ગુજરાતના અમદાવાદ/સુરત કે રાજસ્થાનના જયપુર/જોધપુર) જેથી અમે તમારી સૌથી નજીકનું કેન્દ્ર શોધી શકીએ.",
        "complete": "ખૂબ સરસ! તમારી માહિતી નોંધી લેવામાં આવી છે. હવે અમે તમારા સરનામા અને જિલ્લાના આધારે સૌથી ઉત્તમ 3 સરકારી NSQF તાલીમ અને આજીવિકા વિકલ્પો બતાવી રહ્યા છીએ.",
        "quick_replies": {
            "education": ["8 પાસ", "10 પાસ", "12 પાસ", "શાળાએ ગયા નથી"],
            "skills": ["ઇલેક્ટ્રિક વાયરિંગ", "દરજીકામ", "ખેતી અને પશુપાલન", "બાઇક રિપેરિંગ", "પ્લમ્બિંગ"],
            "interests": ["સોલર એનર્જી", "મોબાઇલ રિપેરિંગ", "ડેરી ફાર્મિંગ", "કપડાં સિલાઇ", "હોસ્પિટાલિટી"],
            "preference": ["પગારવાળી નોકરી (Job)", "પોતાનો ધંધો/સ્વરોજગાર (Business)", "બંને ચાલશે"],
            "location_gj": ["અમદાવાદ", "સુરત", "વડોદરા", "રાજકોટ", "મહેસાણા", "કચ્છ", "ભાવનગર", "આણંદ", "ગાંધીનગર", "જામનગર", "જૂનાગઢ", "દાહોદ", "બનાસકાંઠા", "ભરૂચ", "મોરબી", "નવસારી", "વલસાડ"],
            "location_rj": ["જયપુર", "જોધપુર", "કોટા", "ઉદયપુર", "બીકાનેર", "અજમેર", "અલવર", "ભીલવાડા", "સીકર", "ભરતપુર", "પાલી", "બાડમેર", "નાગૌર", "ચિત્તોડગઢ", "ઝુંઝુનૂ", "શ્રીગંગાનગર"]
        }
    },
    "en": {
        "welcome": "Welcome! I am your PM-AJAY Livelihood & Skilling Assistant. First, which state, district, or PIN code/address do you live in (Gujarat or Rajasthan)? And what is your education level?",
        "ask_education": "What is your education level? (e.g., 8th Pass, 10th Pass, 12th Pass, or No formal schooling?)",
        "ask_skills": "What work have you done previously or what tools/skills do you already know? (e.g., wiring, tailoring, farming, driving?)",
        "ask_interests": "What kind of new trade or business are you interested in learning?",
        "ask_mobility": "How far (in km) can you travel for training or work? Do you have any physical mobility constraints?",
        "ask_preference": "Do you prefer a monthly salary job, or starting your own micro-enterprise with a PM-AJAY GIA grant?",
        "ask_location": "Where do you live? Please provide your state, district, or full address/PIN code (e.g., Gujarat: Ahmedabad/Surat, or Rajasthan: Jaipur/Jodhpur) so we can map nearby centers and job vacancies.",
        "complete": "Wonderful! Your profile and location are recorded. Calculating your top 3 verified NSQF skilling and livelihood pathways for your district now.",
        "quick_replies": {
            "education": ["8th Pass", "10th Pass", "12th Pass", "No Formal Schooling"],
            "skills": ["Electrical wiring", "Tailoring", "Farming & Dairy", "Two-Wheeler Repair", "Masonry"],
            "interests": ["Solar Energy", "Mobile Phone Repair", "Organic Farming", "Garments", "Healthcare"],
            "preference": ["Wage Employment (Job)", "Self Employment (Business)", "Open to Both"],
            "location_gj": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Mehsana", "Kutch", "Bhavnagar", "Anand", "Gandhinagar", "Jamnagar", "Junagadh", "Dahod", "Banaskantha", "Bharuch", "Morbi", "Navsari", "Valsad"],
            "location_rj": ["Jaipur", "Jodhpur", "Kota", "Udaipur", "Bikaner", "Ajmer", "Alwar", "Bhilwara", "Sikar", "Bharatpur", "Pali", "Barmer", "Nagaur", "Chittorgarh", "Jhunjhunu", "Sri Ganganagar"]
        }
    }
}

class AIAgentService:
    def process_turn(
        self,
        user_message: str,
        language: str,
        current_profile: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Tuple[str, BeneficiaryProfileExtract, bool, List[str], List[str], str]:
        """
        Processes a conversational turn.
        Returns:
            - ai_response (spoken text)
            - updated_profile (BeneficiaryProfileExtract)
            - is_profile_complete (bool)
            - missing_fields (List[str])
            - suggested_quick_replies (List[str])
            - next_question_field (str)
        """
        lang = language if language in DIALOGUE_SCRIPTS else "hi"
        script = DIALOGUE_SCRIPTS[lang]

        # 1. Update profile from user message (hybrid: LLM if API key present, otherwise robust regex/rule-based extractor)
        profile_data = self._extract_profile_data(user_message, current_profile, lang)

        # 2. Check missing critical fields — location is first priority!
        missing_fields = []
        if not profile_data.location_state or not profile_data.location_district:
            missing_fields.append("location")
        if not profile_data.education_level:
            missing_fields.append("education_level")
        if not profile_data.existing_skills:
            missing_fields.append("existing_skills")
        if not profile_data.interests:
            missing_fields.append("interests")
        if not profile_data.livelihood_preference:
            missing_fields.append("livelihood_preference")

        # 3. Determine next action
        if not missing_fields:
            # Profile is ready for recommendation!
            return (
                script["complete"],
                profile_data,
                True,
                [],
                [],
                "complete"
            )

        next_field = missing_fields[0]
        if next_field == "location":
            response_text = script["ask_location"]
            # Show location quick replies based on what state they may have mentioned already
            if profile_data.location_state and "raj" in (profile_data.location_state or "").lower():
                quick_replies = script["quick_replies"]["location_rj"]
            else:
                quick_replies = script["quick_replies"]["location_gj"]
        elif next_field == "education_level":
            response_text = script["ask_education"]
            quick_replies = script["quick_replies"]["education"]
        elif next_field == "existing_skills":
            response_text = script["ask_skills"]
            quick_replies = script["quick_replies"]["skills"]
        elif next_field == "interests":
            response_text = script["ask_interests"]
            quick_replies = script["quick_replies"]["interests"]
        elif next_field == "livelihood_preference":
            response_text = script["ask_preference"]
            quick_replies = script["quick_replies"]["preference"]
        else:
            response_text = script["ask_mobility"]
            quick_replies = ["5 km", "15 km", "25 km"]

        return (
            response_text,
            profile_data,
            False,
            missing_fields,
            quick_replies,
            next_field
        )

    def _extract_profile_data(
        self,
        user_message: str,
        current_profile: Dict[str, Any],
        lang: str
    ) -> BeneficiaryProfileExtract:
        """Extracts and merges profile fields using Groq LLM if key exists, or fast local rule parser."""
        groq_key = settings.GROQ_API_KEY
        
        # If Groq API key is available, run LLM extraction
        if groq_key and groq_key.startswith("gsk_"):
            try:
                return self._extract_with_groq(user_message, current_profile, groq_key, lang)
            except Exception as e:
                print(f"LLM extraction fallback to rule-based parser: {e}")

        # Rule-based fallback extractor
        return self._extract_with_rules(user_message, current_profile)

    def _extract_with_groq(
        self,
        user_message: str,
        current_profile: Dict[str, Any],
        api_key: str,
        lang: str
    ) -> BeneficiaryProfileExtract:
        from groq import Groq
        client = Groq(api_key=api_key)

        curr_dict = current_profile.model_dump() if hasattr(current_profile, "model_dump") else dict(current_profile or {})
        prompt = f"""
You are a government beneficiary profiling assistant under PM-AJAY GIA.
Extract beneficiary details from their message.
Existing Profile: {json.dumps(curr_dict)}
User's Latest Statement: "{user_message}"

Extract to JSON matching this exact structure:
{{
  "name": string or null,
  "age": int or null,
  "gender": "Male" | "Female" | "Other" | null,
  "education_level": "No Formal Education" | "Below 8th" | "8th Pass" | "10th Pass" | "12th Pass" | "Graduate" | null,
  "family_occupation": string or null,
  "current_livelihood": string or null,
  "existing_skills": [list of strings],
  "work_experience_years": float,
  "interests": [list of strings],
  "max_travel_distance_km": int,
  "has_mobility_constraint": boolean,
  "livelihood_preference": "Wage Employment" | "Self Employment" | "Both",
  "location_state": "Gujarat" | "Rajasthan" | null,
  "location_district": string or null,
  "location_block": string or null,
  "full_address": string or null,
  "pincode": string or null
}}
Respond ONLY with valid JSON.
"""
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        extract = BeneficiaryProfileExtract(**data)

        # Merge with existing profile ensuring nothing is accidentally lost
        merged = curr_dict.copy()
        for k, v in extract.model_dump(exclude_none=True).items():
            if k in ["existing_skills", "interests"]:
                prev_list = merged.get(k) or []
                for item in v:
                    if item not in prev_list:
                        prev_list.append(item)
                merged[k] = prev_list
            else:
                if v:
                    merged[k] = v

        # If user answered an interest question and LLM put it into skills, copy into interests too!
        if not merged.get("interests") and any(w in user_message.lower() for w in ["रिपेयरिंग", "रिपेयर", "repair", "सीखना", "सोलर", "मोबाइल", "सिलाई", "काम"]):
            user_interest_words = [s for s in (merged.get("existing_skills") or []) if any(w in s.lower() for w in ["repair", "रिपेयर", "mobile", "solar", "tech"])]
            if user_interest_words:
                merged["interests"] = user_interest_words
            elif merged.get("existing_skills"):
                merged["interests"] = list(merged.get("existing_skills"))[:2]

        return BeneficiaryProfileExtract(**merged)

    def _extract_with_rules(self, user_message: str, current_profile: Dict[str, Any]) -> BeneficiaryProfileExtract:
        profile = dict(current_profile or {})
        msg = user_message.lower()

        # Education extraction
        if any(w in msg for w in ["10", "10th", "दसवीं", "૧૦", "દસમી", "matric"]):
            profile["education_level"] = "10th Pass"
        elif any(w in msg for w in ["12", "12th", "बारहवीं", "૧૨", "બારમી", "inter"]):
            profile["education_level"] = "12th Pass"
        elif any(w in msg for w in ["8", "8th", "आठवीं", "૮", "આઠમી"]):
            profile["education_level"] = "8th Pass"
        elif any(w in msg for w in ["5", "5th", "पांचवीं", "૫", "પાંચમી"]):
            profile["education_level"] = "5th Pass"
        elif any(w in msg for w in ["college", "graduate", "बीए", "ગ્રેજ્યુએટ"]):
            profile["education_level"] = "Graduate"
        elif any(w in msg for w in ["पढ़े नहीं", "स्कूले नहीं", "અભણ", "ભણ્યા નથી", "no school", "uneducated"]):
            profile["education_level"] = "Below 8th"

        # Skills extraction
        existing_skills = list(profile.get("existing_skills", []))
        if any(w in msg for w in ["बिजली", "वायर", "इलेक्ट्रिक", "વાયરિંગ", "ઇલેક્ટ્રિક", "wiring", "electric"]):
            if "basic electrical work" not in existing_skills:
                existing_skills.append("basic electrical work")
        if any(w in msg for w in ["सिलाई", "कपड़ा", "टेलर", "દરજી", "સિલાઈ", "tailor", "sewing"]):
            if "hand needlework" not in existing_skills:
                existing_skills.append("hand needlework")
        if any(w in msg for w in ["खेती", "फसल", "किसान", "ખેતી", "ખેડૂત", "farming", "agriculture"]):
            if "farming experience" not in existing_skills:
                existing_skills.append("farming experience")
        if any(w in msg for w in ["गाय", "भैंस", "दूध", "डेयरी", "પશુપાલન", "દૂધ", "dairy", "cattle"]):
            if "livestock rearing" not in existing_skills:
                existing_skills.append("livestock rearing")
        if any(w in msg for w in ["बाइक", "मोटरसाइकिल", "गैरेज", "મિકેનિક", "બાઇક", "garage", "bike", "two wheeler"]):
            if "spanner and socket tool usage" not in existing_skills:
                existing_skills.append("spanner and socket tool usage")
        if any(w in msg for w in ["नल", "प्लंबर", "पाइप", "પ્લમ્બર", "પાણી પાઇપ", "plumber", "pipe"]):
            if "pipe cutting and plumbing" not in existing_skills:
                existing_skills.append("pipe cutting and plumbing")
        if any(w in msg for w in ["राजमिस्त्री", "चिनाई", "मकान", "કડિયો", "ચણતર", "mason", "construction"]):
            if "sand cement mixing" not in existing_skills:
                existing_skills.append("sand cement mixing")
        if any(w in msg for w in ["ड्राइवर", "गाड़ी चलाना", "ડ્રાઇવિંગ", "વાહન", "driver", "driving"]):
            if "road sense and driving" not in existing_skills:
                existing_skills.append("road sense and driving")
        profile["existing_skills"] = existing_skills

        # Interests extraction
        interests = list(profile.get("interests", []))
        if any(w in msg for w in ["सोलर", "धूप", "સોલર", "solar"]):
            if "solar systems" not in interests:
                interests.append("solar systems")
        if any(w in msg for w in ["मोबाइल", "ફોન", "mobile", "phone"]):
            if "mobile phones" not in interests:
                interests.append("mobile phones")
        if any(w in msg for w in ["दुकान", "सिलाई", "બુટિક", "tailoring", "boutique"]):
            if "sewing" not in interests:
                interests.append("sewing")
        if any(w in msg for w in ["दूध", "ડેરી", "dairy", "milk"]):
            if "dairy animals" not in interests:
                interests.append("dairy animals")
        if any(w in msg for w in ["कंप्यूटर", "કેમેરા", "cctv", "camera"]):
            if "security cameras" not in interests:
                interests.append("security cameras")
        if any(w in msg for w in ["हॉस्पिटल", "मरीज", "દવાખાનું", "nurse", "hospital"]):
            if "healthcare" not in interests:
                interests.append("healthcare")
        if not interests and len(existing_skills) > 0:
            # Transfer skill to interest if user talks enthusiastically
            interests.extend(existing_skills[:2])
        profile["interests"] = interests

        # Preference extraction
        if any(w in msg for w in ["दुकान", "खुद का", "बिजनेस", "ધંધો", "પોતાનું", "business", "self"]):
            profile["livelihood_preference"] = "Self Employment"
        elif any(w in msg for w in ["नौकरी", "सैलरी", "कंपनी", "નોકરી", "પગાર", "job", "salary"]):
            profile["livelihood_preference"] = "Wage Employment"
        elif any(w in msg for w in ["दोनों", "કાંઈ પણ", "both", "either"]):
            profile["livelihood_preference"] = "Both"

        # Mobility constraint
        if any(w in msg for w in ["दिव्यांग", "पैर", "चलने में दिक्कत", "વિકલાંગ", "ચાલવામાં તકલીફ", "handicap", "disabled", "cannot walk"]):
            profile["has_mobility_constraint"] = True
            profile["max_travel_distance_km"] = 5

        # Years of experience extraction
        years_match = re.search(r'(\d+)\s*(साल|वर्ष|વર્ષ|year)', msg)
        if years_match:
            profile["work_experience_years"] = float(years_match.group(1))

        # ----- LOCATION EXTRACTION (State + District + PIN + Full Address) -----
        # Comprehensive Gujarat districts (33 districts, blocks, cities)
        GJ_DISTRICTS = {
            "ahmedabad": "Ahmedabad", "amdavad": "Ahmedabad", "अहमदाबाद": "Ahmedabad", "અમદાવાદ": "Ahmedabad", "sanand": "Ahmedabad", "viramgam": "Ahmedabad", "dholka": "Ahmedabad", "bavla": "Ahmedabad",
            "amreli": "Amreli", "अमरेली": "Amreli", "અમરેલી": "Amreli", "rajula": "Amreli", "lathi": "Amreli", "jafrabad": "Amreli",
            "anand": "Anand", "आनंद": "Anand", "આણંદ": "Anand", "borsad": "Anand", "petlad": "Anand", "khambhat": "Anand",
            "aravalli": "Aravalli", "अरावली": "Aravalli", "અરવલ્લી": "Aravalli", "modasa": "Aravalli", "bayad": "Aravalli", "malpur": "Aravalli",
            "banaskantha": "Banaskantha", "बनासकांठा": "Banaskantha", "બનાસકાંઠા": "Banaskantha", "palanpur": "Banaskantha", "deesa": "Banaskantha", "danta": "Banaskantha", "tharad": "Banaskantha",
            "bharuch": "Bharuch", "भरूच": "Bharuch", "ભરૂચ": "Bharuch", "ankleshwar": "Bharuch", "jhagadia": "Bharuch", "dahej": "Bharuch",
            "bhavnagar": "Bhavnagar", "भावनगर": "Bhavnagar", "ભાવનગર": "Bhavnagar", "alang": "Bhavnagar", "sihor": "Bhavnagar", "palitana": "Bhavnagar",
            "botad": "Botad", "बोटाद": "Botad", "બોટાદ": "Botad", "gadhada": "Botad", "barwala": "Botad",
            "chhota udaipur": "Chhota Udaipur", "छोटा उदयपुर": "Chhota Udaipur", "છોટા ઉદેપુર": "Chhota Udaipur", "bodeli": "Chhota Udaipur", "sankheda": "Chhota Udaipur",
            "dahod": "Dahod", "दाहोद": "Dahod", "દાહોદ": "Dahod", "jhalod": "Dahod", "limkheda": "Dahod", "devgadh baria": "Dahod",
            "dang": "Dang", "डांग": "Dang", "ડાંગ": "Dang", "ahwa": "Dang", "waghai": "Dang", "subir": "Dang",
            "devbhumi dwarka": "Devbhumi Dwarka", "dwarka": "Devbhumi Dwarka", "द्वारका": "Devbhumi Dwarka", "દ્વારકા": "Devbhumi Dwarka", "khambhalia": "Devbhumi Dwarka",
            "gandhinagar": "Gandhinagar", "गांधीनगर": "Gandhinagar", "ગાંધીનગર": "Gandhinagar", "kalol": "Gandhinagar", "mansa": "Gandhinagar", "dehgam": "Gandhinagar",
            "gir somnath": "Gir Somnath", "गिर सोमनाथ": "Gir Somnath", "ગીર સોમનાથ": "Gir Somnath", "veraval": "Gir Somnath", "somnath": "Gir Somnath", "talala": "Gir Somnath", "kodinar": "Gir Somnath",
            "jamnagar": "Jamnagar", "जामनगर": "Jamnagar", "જામનગર": "Jamnagar", "dhrol": "Jamnagar", "lalpur": "Jamnagar",
            "junagadh": "Junagadh", "जूनागढ़": "Junagadh", "જૂનાગઢ": "Junagadh", "keshod": "Junagadh", "mangrol": "Junagadh", "visavadar": "Junagadh",
            "kheda": "Kheda", "खेड़ा": "Kheda", "ખેડા": "Kheda", "nadiad": "Kheda", "નડિયાદ": "Kheda", "kapadvanj": "Kheda",
            "kutch": "Kutch", "कच्छ": "Kutch", "કચ્છ": "Kutch", "bhuj": "Kutch", "भुज": "Kutch", "ભુજ": "Kutch", "gandhidham": "Kutch", "mandvi": "Kutch", "anjar": "Kutch",
            "mahisagar": "Mahisagar", "महिसागर": "Mahisagar", "મહીસાગર": "Mahisagar", "lunawada": "Mahisagar", "santrampur": "Mahisagar",
            "mehsana": "Mehsana", "मेहसाणा": "Mehsana", "મહેસાણા": "Mehsana", "kadi": "Mehsana", "unjha": "Mehsana", "visnagar": "Mehsana",
            "morbi": "Morbi", "मोरबी": "Morbi", "મોરબી": "Morbi", "wankaner": "Morbi", "halvad": "Morbi",
            "narmada": "Narmada", "नर्मदा": "Narmada", "નર્મદા": "Narmada", "rajpipla": "Narmada", "kevadia": "Narmada", "dediapada": "Narmada",
            "navsari": "Navsari", "नवसारी": "Navsari", "નવસારી": "Navsari", "gandevi": "Navsari", "jalalpore": "Navsari", "chikhli": "Navsari",
            "panchmahal": "Panchmahal", "पंचमहल": "Panchmahal", "પંચમહાલ": "Panchmahal", "godhra": "Panchmahal", "गोधरा": "Panchmahal", "ગોધરા": "Panchmahal", "halol": "Panchmahal", "हालोल": "Panchmahal", "હાલોલ": "Panchmahal",
            "patan": "Patan", "पाटन": "Patan", "પાટણ": "Patan", "sidhpur": "Patan", "radhanpur": "Patan",
            "porbandar": "Porbandar", "पोरबंदर": "Porbandar", "પોરબંદર": "Porbandar", "ranavav": "Porbandar", "kutiyana": "Porbandar",
            "rajkot": "Rajkot", "राजकोट": "Rajkot", "રાજકોટ": "Rajkot", "shapar": "Rajkot", "lodhika": "Rajkot", "gondal": "Rajkot", "jetpur": "Rajkot",
            "sabarkantha": "Sabarkantha", "साबरकांठा": "Sabarkantha", "સાબરકાંઠા": "Sabarkantha", "himatnagar": "Sabarkantha", "idar": "Sabarkantha", "prantij": "Sabarkantha",
            "surat": "Surat", "सूरत": "Surat", "સુરત": "Surat", "sachin": "Surat", "hazira": "Surat", "bardoli": "Surat", "kamrej": "Surat",
            "surendranagar": "Surendranagar", "सुरेंद्रनगर": "Surendranagar", "સુરેન્દ્રનગર": "Surendranagar", "wadhwan": "Surendranagar", "chotila": "Surendranagar", "dhrangadhra": "Surendranagar",
            "tapi": "Tapi", "तापी": "Tapi", "તાપી": "Tapi", "vyara": "Tapi", "songadh": "Tapi", "valod": "Tapi",
            "vadodara": "Vadodara", "baroda": "Vadodara", "वडोदरा": "Vadodara", "વડોદરા": "Vadodara", "savli": "Vadodara", "padra": "Vadodara", "waghodia": "Vadodara",
            "valsad": "Valsad", "वलसाड": "Valsad", "વલસાડ": "Valsad", "vapi": "Valsad", "वापी": "Valsad", "વાપી": "Valsad", "umbergaon": "Valsad"
        }
        # Comprehensive Rajasthan districts (33 districts, blocks, cities)
        RJ_DISTRICTS = {
            "ajmer": "Ajmer", "अजमेर": "Ajmer", "અજમેર": "Ajmer", "kishangarh": "Ajmer", "beawar": "Ajmer",
            "alwar": "Alwar", "अलवर": "Alwar", "અલ્વર": "Alwar", "bhiwadi": "Alwar", "neemrana": "Alwar", "tijara": "Alwar",
            "banswara": "Banswara", "बांसवाड़ा": "Banswara", "બાંસવાડા": "Banswara", "kushalgarh": "Banswara", "ghatol": "Banswara",
            "baran": "Baran", "बारां": "Baran", "બારાં": "Baran", "antah": "Baran", "chhabra": "Baran",
            "barmer": "Barmer", "बाड़मेर": "Barmer", "બાડમેર": "Barmer", "balotra": "Barmer", "baytu": "Barmer",
            "bharatpur": "Bharatpur", "भरतपुर": "Bharatpur", "ભરતપુર": "Bharatpur", "deeg": "Bharatpur", "bayana": "Bharatpur", "sewar": "Bharatpur",
            "bhilwara": "Bhilwara", "भीलवाड़ा": "Bhilwara", "ભીલવાડા": "Bhilwara", "mandal": "Bhilwara", "suwana": "Bhilwara", "gulabpura": "Bhilwara",
            "bikaner": "Bikaner", "बीकानेर": "Bikaner", "બીકાનેર": "Bikaner", "beechwal": "Bikaner", "nokha": "Bikaner", "kolayat": "Bikaner",
            "bundi": "Bundi", "बूंदी": "Bundi", "બૂંદી": "Bundi", "keshoraipatan": "Bundi", "hindoli": "Bundi",
            "chittorgarh": "Chittorgarh", "चित्तौड़गढ़": "Chittorgarh", "ચિત્તોડગઢ": "Chittorgarh", "nimbahera": "Chittorgarh", "rawatbhata": "Chittorgarh",
            "churu": "Churu", "चूरू": "Churu", "ચૂરુ": "Churu", "ratangarh": "Churu", "sujangarh": "Churu", "sardarshahar": "Churu",
            "dausa": "Dausa", "दौसा": "Dausa", "દૌસા": "Dausa", "bandikui": "Dausa", "lalsot": "Dausa",
            "dholpur": "Dholpur", "धौलपुर": "Dholpur", "ધોલપુર": "Dholpur", "bari": "Dholpur", "rajakhera": "Dholpur",
            "dungarpur": "Dungarpur", "डूंगरपुर": "Dungarpur", "ડુંગરપુર": "Dungarpur", "sagwara": "Dungarpur", "aspur": "Dungarpur",
            "hanumangarh": "Hanumangarh", "हनुमानगढ़": "Hanumangarh", "હનુમાનગઢ": "Hanumangarh", "rawatsar": "Hanumangarh", "nohar": "Hanumangarh",
            "jaipur": "Jaipur", "जयपुर": "Jaipur", "જયપુર": "Jaipur", "sanganer": "Jaipur", "sitapura": "Jaipur", "jhotwara": "Jaipur", "vkia": "Jaipur",
            "jaisalmer": "Jaisalmer", "जैसलमेर": "Jaisalmer", "જેસલમેર": "Jaisalmer", "pokhran": "Jaisalmer", "fatehgarh": "Jaisalmer",
            "jalore": "Jalore", "जालौर": "Jalore", "જાલોર": "Jalore", "bhinmal": "Jalore", "sanchore": "Jalore",
            "jhalawar": "Jhalawar", "झालावाड़": "Jhalawar", "ઝાલાવાડ": "Jhalawar", "jhalrapatan": "Jhalawar",
            "jhunjhunu": "Jhunjhunu", "झुंझुनू": "Jhunjhunu", "ઝુંઝુનૂ": "Jhunjhunu", "chirawa": "Jhunjhunu", "nawalgarh": "Jhunjhunu", "khetri": "Jhunjhunu",
            "jodhpur": "Jodhpur", "जोधपुर": "Jodhpur", "જોધપુર": "Jodhpur", "boronada": "Jodhpur", "basni": "Jodhpur", "mandore": "Jodhpur",
            "karauli": "Karauli", "करौली": "Karauli", "કરોલી": "Karauli", "hindaun": "Karauli", "todabhim": "Karauli",
            "kota": "Kota", "कोटा": "Kota", "કોટા": "Kota", "ranpur": "Kota", "dcm": "Kota", "ladpura": "Kota",
            "nagaur": "Nagaur", "नागौर": "Nagaur", "નાગૌર": "Nagaur", "makrana": "Nagaur", "kuchaman": "Nagaur", "merta": "Nagaur",
            "pali": "Pali", "पाली": "Pali", "પાલી": "Pali", "sojat": "Pali", "sumerpur": "Pali",
            "pratapgarh": "Pratapgarh", "प्रतापगढ़": "Pratapgarh", "પ્રતાપગઢ": "Pratapgarh", "arnod": "Pratapgarh", "dhariyawad": "Pratapgarh",
            "rajsamand": "Rajsamand", "राजसमंद": "Rajsamand", "રાજસમંદ": "Rajsamand", "nathdwara": "Rajsamand", "amet": "Rajsamand",
            "sawai madhopur": "Sawai Madhopur", "सवाई माधोपुर": "Sawai Madhopur", "સવાઈ માધોપુર": "Sawai Madhopur", "gangapur": "Sawai Madhopur",
            "sikar": "Sikar", "सीकर": "Sikar", "સીકર": "Sikar", "reengus": "Sikar", "ringas": "Sikar", "fatehpur": "Sikar", "neem ka thana": "Sikar",
            "sirohi": "Sirohi", "सिरोही": "Sirohi", "સિરોહી": "Sirohi", "abu road": "Sirohi", "mount abu": "Sirohi", "sheoganj": "Sirohi",
            "sri ganganagar": "Sri Ganganagar", "ganganagar": "Sri Ganganagar", "श्रीगंगानगर": "Sri Ganganagar", "શ્રીગંગાનગર": "Sri Ganganagar", "suratgarh": "Sri Ganganagar",
            "tonk": "Tonk", "टोंक": "Tonk", "ટોંક": "Tonk", "niwai": "Tonk", "deoli": "Tonk",
            "udaipur": "Udaipur", "उदयपुर": "Udaipur", "ઉદયપુર": "Udaipur", "sukher": "Udaipur", "fatehpura": "Udaipur"
        }
        
        # Detect state first
        is_gujarat = any(w in msg for w in ["gujarat", "गुजरात", "ગુજરાત", "gujrat"])
        is_rajasthan = any(w in msg for w in ["rajasthan", "राजस्थान", "રાજસ્થાન", "rajsthan"])
        
        if is_gujarat and not profile.get("location_state"):
            profile["location_state"] = "Gujarat"
        if is_rajasthan and not profile.get("location_state"):
            profile["location_state"] = "Rajasthan"

        # Detect district
        if not profile.get("location_district"):
            for key, district_name in GJ_DISTRICTS.items():
                if key in msg:
                    profile["location_district"] = district_name
                    if not profile.get("location_state"):
                        profile["location_state"] = "Gujarat"
                    break
            for key, district_name in RJ_DISTRICTS.items():
                if key in msg:
                    profile["location_district"] = district_name
                    if not profile.get("location_state"):
                        profile["location_state"] = "Rajasthan"
                    break

        # Extract 6-digit Indian postal PIN code
        pincode_match = re.search(r'\b([1-9][0-9]{5})\b', msg)
        if pincode_match:
            pin = pincode_match.group(1)
            profile["pincode"] = pin
            # Gujarat PIN codes typically start with 36, 37, 38, 39
            if pin.startswith(("36", "37", "38", "39")) and not profile.get("location_state"):
                profile["location_state"] = "Gujarat"
            # Rajasthan PIN codes typically start with 30, 31, 32, 33, 34
            elif pin.startswith(("30", "31", "32", "33", "34")) and not profile.get("location_state"):
                profile["location_state"] = "Rajasthan"

        # Extract full address sentence if user describes their address/mohalla/village
        addr_keywords = ["address", "पता", "સરનામું", "रहता हूँ", "रहती हूँ", "રહું છું", "गाँव", "गांव", "ગામ", "तहसील", "तालुका", "mohalla", "colony", "ward", "वार्ड", "વોર્ડ", "गली", "गल्ली"]
        if any(w in msg for w in addr_keywords):
            profile["full_address"] = user_message.strip()

        return BeneficiaryProfileExtract(**profile)

ai_agent = AIAgentService()
