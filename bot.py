import asyncio
import os
from playwright.async_api import async_playwright

LOGIN_URL     = "https://aternos.org/go/"           # ← page d'accueil
DASHBOARD_URL = "https://aternos.org/servers/" # ← page liste des serveurs
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

SERVER_ID = "lWzJvuqIhoHMRRcl"

# Login
LOGIN_BUTTON_SELECTOR = "button.login-button.btn.btn-main.join-left"
USERNAME_SELECTOR     = "input.username"
PASSWORD_SELECTOR     = "input.password"
SUBMIT_SELECTOR       = "button[type='submit']"

# Serveur
SERVER_SELECTOR  = f"div.server-body[data-id='{SERVER_ID}']"
START_SELECTOR   = "button#start.btn.btn-huge.btn-success"
TIMER_SELECTOR   = "div.server-end-countdown"
BOUTON_SELECTOR  = "button.btn.btn-tiny.btn-success.server-extend-end"

async def login(page):
    print("🔐 Connexion en cours...")
    await page.goto(LOGIN_URL)
    await page.click(LOGIN_BUTTON_SELECTOR)
    await page.wait_for_selector(USERNAME_SELECTOR, state="visible", timeout=5000)
    await page.fill(USERNAME_SELECTOR, USERNAME)
    await page.fill(PASSWORD_SELECTOR, PASSWORD)
    await page.click(SUBMIT_SELECTOR)
    await page.wait_for_load_state("networkidle")
    print("✅ Connecté !")

async def aller_sur_serveur(page):
    print("🔍 Recherche du serveur...")
    await page.goto(DASHBOARD_URL)
    await page.wait_for_selector(SERVER_SELECTOR, state="visible", timeout=10000)
    await page.click(SERVER_SELECTOR)
    await page.wait_for_load_state("networkidle")
    print("✅ Sur la page du serveur !")

async def demarrer_si_besoin(page):
    try:
        # Vérifie si le bouton "Démarrer" est présent
        start_btn = await page.query_selector(START_SELECTOR)
        if start_btn:
            visible = await start_btn.is_visible()
            if visible:
                print("▶️ Serveur arrêté, clic sur Démarrer...")
                await start_btn.click()
                # Attend que le serveur démarre (le bouton disparaît et le timer apparaît)
                await page.wait_for_selector(START_SELECTOR, state="hidden", timeout=60000)
                print("✅ Serveur démarré !")
            else:
                print("✅ Serveur déjà en cours, passage à la surveillance...")
        else:
            print("✅ Serveur déjà en cours, passage à la surveillance...")
    except Exception as e:
        print(f"⚠️ Erreur vérification démarrage : {e}")

async def surveiller_et_cliquer(page):
    print("👀 Surveillance du timer...")

    while True:
        try:
            # Vérifie si le serveur s'est arrêté (bouton Démarrer réapparu)
            start_btn = await page.query_selector(START_SELECTOR)
            if start_btn and await start_btn.is_visible():
                print("\n⚠️ Serveur arrêté ! Redémarrage...")
                await start_btn.click()
                await page.wait_for_selector(START_SELECTOR, state="hidden", timeout=60000)
                print("✅ Serveur redémarré !")
                await asyncio.sleep(2)
                continue

            # Lecture du timer
            timer_el = await page.query_selector(TIMER_SELECTOR)
            if timer_el:
                timer_text = (await timer_el.inner_text()).strip()
                print(f"⏱️ Timer : {timer_text}", end="\r")

                if timer_text == "1:00":
                    print("\n🎯 Timer à 1:00 ! Clic sur le bouton...")
                    await page.wait_for_selector(BOUTON_SELECTOR, state="visible", timeout=5000)
                    await page.click(BOUTON_SELECTOR)
                    print("✅ Bouton cliqué ! Reprise de la surveillance...")
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"\n⚠️ Erreur : {e}")

        await asyncio.sleep(0.5)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await login(page)
        await aller_sur_serveur(page)
        await demarrer_si_besoin(page)
        await surveiller_et_cliquer(page)

        await browser.close()

asyncio.run(main())
