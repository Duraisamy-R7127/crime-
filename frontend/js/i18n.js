const translations = {
    "en": {
        "title_home": "Home",
        "title_voice": "Voice",
        "title_analytics": "Analytics",
        "title_predict": "Predict",
        "title_map": "Map",
        "title_deploy": "Deploy",
        "title_legal": "Legal",
        "title_alerts": "Alerts",
        "dashboard_title": "Command Dashboard",
        "dashboard_desc": "State-wide crime posture at a glance",
        "stat_crimes": "Crimes · YTD",
        "stat_active": "Active Cases",
        "stat_response": "Avg Response Time",
        "stat_disposal": "Case Disposal Rate",
        "btn_new_fir": "New FIR",
        "voice_title": "Voice Assistant",
        "voice_hint": "Tap to speak — try 'Top 5 dangerous districts this month'",
    },
    "ta": {
        "title_home": "முகப்பு",
        "title_voice": "குரல்",
        "title_analytics": "பகுப்பாய்வு",
        "title_predict": "கணிப்பு",
        "title_map": "வரைபடம்",
        "title_deploy": "படையெடுப்பு",
        "title_legal": "சட்டம்",
        "title_alerts": "எச்சரிக்கைகள்",
        "dashboard_title": "கட்டளை டாஷ்போர்டு",
        "dashboard_desc": "தமிழ்நாடு மாநில குற்ற நிலவரம்",
        "stat_crimes": "குற்றங்கள் · YTD",
        "stat_active": "நடப்பு வழக்குகள்",
        "stat_response": "சராசரி பதிலளிப்பு நேரம்",
        "stat_disposal": "வழக்கு தீர்வு விகிதம்",
        "btn_new_fir": "புதிய FIR",
        "voice_title": "குரல் உதவியாளர்",
        "voice_hint": "பேச தட்டவும் — 'இந்த மாதம் அதிக ஆபத்தான 5 மாவட்டங்கள்' என முயற்சிக்கவும்",
    },
    "hi": {
        "title_home": "मुख्य पृष्ठ",
        "title_voice": "आवाज़",
        "title_analytics": "विश्लेषण",
        "title_predict": "भविष्यवाणी",
        "title_map": "नक्शा",
        "title_deploy": "तैनाती",
        "title_legal": "कानूनी",
        "title_alerts": "अलर्ट",
        "dashboard_title": "कमांड डैशबोर्ड",
        "dashboard_desc": "तमिलनाडु राज्यव्यापी अपराध स्थिति",
        "stat_crimes": "अपराध · YTD",
        "stat_active": "सक्रिय मामले",
        "stat_response": "औसत प्रतिक्रिया समय",
        "stat_disposal": "मामला निपटान दर",
        "btn_new_fir": "नया FIR",
        "voice_title": "वॉयस असिस्टेंट",
        "voice_hint": "बोलने के लिए टैप करें — 'इस महीने के शीर्ष 5 खतरनाक जिले' आज़माएं",
    }
};

let currentLang = "en";

function changeLanguage(langCode) {
    if (langCode.startsWith("ta")) currentLang = "ta";
    else if (langCode.startsWith("hi")) currentLang = "hi";
    else currentLang = "en";
    
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[currentLang][key]) {
            el.innerText = translations[currentLang][key];
        }
    });
}
