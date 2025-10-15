from dotenv import load_dotenv

load_dotenv() 

import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from app.menus.util import clear_screen, pause
from app.client.engsel import *
from app.client.engsel2 import get_tiering_info
from app.menus.payment import show_transaction_history
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.banner import show_banner
from app.menus.package import fetch_my_packages, get_packages_by_family
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.service.sentry import enter_sentry_mode
from app.menus.purchase import purchase_by_family

console = Console()

def show_main_menu(profile):
    """Displays the main menu with a cyberpunk theme using rich."""
    clear_screen()

    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")

    profile_text = Text.assemble(
        ("Nomor         : ", "bold cyan"), (f"{profile['number']}\n", "white"),
        ("Tipe          : ", "bold cyan"), (f"{profile['subscription_type']}\n\n", "white"),
        ("Pulsa         : ", "bold green"), (f"Rp {profile['balance']}\n", "white"),
        ("Masa Aktif    : ", "bold green"), (f"{expired_at_dt}\n\n", "white"),
        (f"{profile['point_info']}", "bold yellow")
    )

    console.print(Panel(
        profile_text,
        title="[bold magenta]--[ User Profile ]--[/bold magenta]",
        border_style="bold green",
        padding=(1, 2)
    ))

    menu_text = Text.assemble(
        (" 1.", "bold yellow"), (" Login/Ganti akun\n", "white"),
        (" 2.", "bold yellow"), (" Lihat Paket Saya\n", "white"),
        (" 3.", "bold yellow"), (" Beli Paket ", "white"), ("🔥 HOT 🔥\n", "bold red"),
        (" 4.", "bold yellow"), (" Beli Paket ", "white"), ("🔥 HOT-2 🔥\n", "bold red"),
        (" 5.", "bold yellow"), (" Beli Paket Berdasarkan Family Code\n", "white"),
        (" 6.", "bold yellow"), (" Riwayat Transaksi\n\n", "white"),
        (" 7.", "bold yellow"), (" [Test] Purchase all packages in family code\n", "grey50"),
        ("00.", "bold yellow"), (" Bookmark Paket\n\n", "white"),
        ("99.", "bold red"),   (" Tutup aplikasi", "white")
    )

    console.print(Panel(
        menu_text,
        title="[bold magenta]--[ Main Menu ]--[/bold magenta]",
        border_style="bold green",
        padding=(1, 2)
    ))

show_menu = True
def main():
    show_banner()
    while True:
        active_user = AuthInstance.get_active_user()

        # Logged in
        if active_user is not None:
            balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
            balance_remaining = balance.get("remaining")
            balance_expired_at = balance.get("expired_at")
            
            profile_data = get_profile(AuthInstance.api_key, active_user["tokens"]["access_token"], active_user["tokens"]["id_token"])
            sub_id = profile_data["profile"]["subscriber_id"]
            sub_type = profile_data["profile"]["subscription_type"]
            
            point_info = "Points: N/A | Tier: N/A"
            
            if sub_type == "PREPAID":
                tiering_data = get_tiering_info(AuthInstance.api_key, active_user["tokens"])
                tier = tiering_data.get("tier", 0)
                current_point = tiering_data.get("current_point", 0)
                point_info = f"Points: {current_point} | Tier: {tier}"
            
            profile = {
                "number": active_user["number"],
                "subscriber_id": sub_id,
                "subscription_type": sub_type,
                "balance": balance_remaining,
                "balance_expired_at": balance_expired_at,
                "point_info": point_info
            }

            show_main_menu(profile)

            choice = console.input("[bold yellow]Pilih menu > [/bold yellow]")
            if choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                else:
                    print("No user selected or failed to load user.")
                continue
            elif choice == "2":
                fetch_my_packages()
                continue
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code)
            elif choice == "6":
                show_transaction_history(AuthInstance.api_key, active_user["tokens"])
            elif choice == "7":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                use_decoy = input("Use decoy package? (y/n): ").lower() == 'y'
                pause_on_success = input("Pause on each successful purchase? (y/n): ").lower() == 'y'
                purchase_by_family(family_code, use_decoy, pause_on_success)
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            elif choice == "t":
                res = get_package(
                    AuthInstance.api_key,
                    active_user["tokens"],
                    ""
                )
                print(json.dumps(res, indent=2))
                input("Press Enter to continue...")
                pass
            elif choice == "s":
                enter_sentry_mode()
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # Not logged in
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
            else:
                print("No user selected or failed to load user.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
