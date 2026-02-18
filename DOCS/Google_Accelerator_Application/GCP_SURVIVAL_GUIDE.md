# Solo Dev's Guide to the Google Ecosystem (GCP)

## 1. The "Easy Mode" Stack (Use This First)
Google Cloud Platform (GCP) has 100+ services. You only need **three** to start. Ignore the rest.

### A. Vertex AI Studio (The Brain)
*   **What it is:** A web dashboard where you can type prompts into Gemini Pro/Ultra and see results immediately, without writing code.
*   **Why it helps:** You can "test" your game logic (NPC dialogue, quest generation) here first. Once it works, you click "Get Code" and it gives you the TypeScript to copy-paste into `eideus-server`.
*   **Solo Dev Hack:** Use "Prompt Management" to save your best system prompts so you don't lose them.

### B. Firebase (The Backend)
*   **What it is:** Google's "Serverless" platform for mobile/web apps.
*   **Why it helps:**
    *   **Auth:** Handles "Log in with Google" for you. (10 minutes to setup).
    *   **Firestore:** A NoSQL database (like your JSON files) that lives in the cloud. Perfect for syncing player save states.
    *   **Hosting:** Hosts your React frontend (`dawn-ui`) with one command: `firebase deploy`.

### C. Cloud Run (The Server)
*   **What it is:** Where your `eideus-server` (the Hybrid Router) will live.
*   **Why it helps:**
    *   **Scales to Zero:** If no one is playing, it shuts down. **Cost: $0.**
    *   **Auto-scaling:** If 10,000 people log in, it instantly creates 500 copies of your server to handle the load. You don't have to manage machines.

---

## 2. The "AI Force Multiplier"
Since you don't write code manually, you should lean into **Gemini Code Assist**.
*   **What it is:** It's like Copilot, but it knows your entire GCP project context.
*   **How to use it:** You can ask it questions like "How do I connect my local `eideus-server` to Vertex AI?" and it will generate the specific boilerplate code for you.
*   **Project IDX:** Google's new browser-based IDE (like VS Code in the cloud). It comes pre-configured with AI tools. You might like moving your dev environment here so you can code from any machine (iPad, Laptop, Library PC).

---

## 3. The "Danger Zone" (Cost Control)
**Credits are finite.** Do not accidentally burn $350k.
*   **Rule #1: Never use raw Compute Engine (VMs) unless you must.** Using `Cloud Run` prevents you from leaving a $5,000/month GPU server running overnight by mistake.
*   **Rule #2: Set Budget Alerts.** Go to "Billing" -> "Budgets & Alerts". Set an alert at $100/month. If your code goes crazy, Google emails you immediately.
