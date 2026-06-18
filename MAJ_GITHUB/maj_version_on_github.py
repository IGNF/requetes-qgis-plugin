import os
import re
import subprocess
import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QInputDialog, QApplication, QDialog, QTableWidgetItem, QMessageBox

GIT_EXE = r"C:\Users\gpecheur\AppData\Local\Programs\Git\cmd\git.exe"

def get_all_branch():
    try:
        result = subprocess.run([GIT_EXE, 'branch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(result.stderr)
            return [], None
        branches = []
        current = None
        for line in result.stdout.splitlines():
            line = line.strip()
            # ignorer les états detached HEAD
            if "(HEAD detached" in line:
                continue
            if line.startswith("*"):
                branch_name = line[2:].strip()
                current = branch_name
                branches.append(branch_name)
            else:
                branches.append(line)
        return branches, current
    except Exception:
        import traceback
        traceback.print_exc()
        return [], None


class GitManagerDialog(QDialog):
    def __init__(self):
        super().__init__()
        # branche active
        self.branch_active = None
        # branche sélectionnée
        self.selected_branch = None
        # branches distantes absentes en local
        self.branches_manquantes = None

        # branches protégées (non supprimables)
        self.protected = ["main", "master", "develop"]

        loadUi(os.path.join(os.path.dirname(__file__), "main.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        current = os.path.dirname(__file__)
        parent = os.path.dirname(current)
        plugin = os.path.basename(parent)
        self.setWindowTitle(plugin)
        self.label_repository.setText(f"Repository : <b><font color='blue'>{plugin}</font></b>")

        self.tableWidget_branche.setShowGrid(False)
        self.tableWidget_branche.verticalHeader().setVisible(False)
        self.tableWidget_branche.horizontalHeader().setVisible(False)
        self.tableWidget_branche.setEditTriggers(self.tableWidget_branche.NoEditTriggers)
        self.tableWidget_branche.itemDoubleClicked.connect(self.on_branch_double_click)
        self.tableWidget_branche.itemClicked.connect(self.on_branch_simple_click)


        # branches distantes
        self.tableWidget_branche_distantes.setShowGrid(False)
        self.tableWidget_branche_distantes.verticalHeader().setVisible(False)
        self.tableWidget_branche_distantes.horizontalHeader().setVisible(False)
        self.tableWidget_branche_distantes.setEditTriggers(self.tableWidget_branche.NoEditTriggers)
        self.tableWidget_branche_distantes.itemClicked.connect(self.on_branch_simple_click)



        self.pushButton_status.clicked.connect(self.on_status)
        self.pushButton_status_commit.clicked.connect(self.on_status_commit)
        self.pushButton_maj_branch.clicked.connect(self.on_maj_branch)
        self.pushButton_maj_from_branche_sel.clicked.connect(self.on_maj_branch_from_selected_branch)
        self.pushButton_new_branch.clicked.connect(self.on_create_new_branch)
        self.pushButton_suppr_branche.clicked.connect(self.on_suppr_branche)
        self.pushButton_merge_release.clicked.connect(self.on_merge_release)

    def run_git(self, args, check=True):
        current = os.path.dirname(__file__)
        parent = os.path.dirname(current)
        try:
            result = subprocess.run(
                [GIT_EXE] + args,
                cwd=parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                # erreur ignorée
                if not check:
                    print(result.stderr.strip())
                    return result
                # erreur bloquante
                QMessageBox.critical(
                    self,
                    "Erreur Git",
                    result.stderr.strip()
                    if result.stderr
                    else f"Erreur inconnue Git : {args}"
                )
                return None
            return result
        except Exception as e:
            QMessageBox.critical(self, "Erreur Python", str(e))
        return None

    def get_modified_files(self):
        res = self.run_git(["status", "--porcelain"])
        if not res:
            return None
        lines = res.stdout.strip().splitlines()
        if not lines:
            return None
        files = []
        for line in lines:
            # format : " M metadata.txt"
            filepath = line[3:]
            files.append(filepath)
        return files

    def on_status(self):
        res = self.run_git(["status"])
        if not res:
            return False
        QMessageBox.information(self, "Git Status", res.stdout.strip())
        return True

    def on_status_commit(self):
        # fetch
        self.run_git(["fetch"])

        # Calcul ahead / behind
        res = self.run_git([
            "rev-list", "--left-right", "--count",
            f"refs/remotes/origin/{self.branch_active}...refs/heads/{self.branch_active}"])

        if not res:
            QMessageBox.critical(self, "git", "Impossible de déterminer l'état de la branche.")
            return False

        behind, ahead = map(int, res.stdout.strip().split())

        # Divergence
        if ahead > 0 and behind > 0:
            message = "La branche a divergé (pull puis push nécessaires).\nVoulez-vous effectuer un pull + push ?"
            if QMessageBox.question(self, "git", message) == QMessageBox.Yes:
                if not self.run_git(["pull","origin", f"refs/heads/{self.branch_active}"]):
                    return False
                if not self.run_git(["push","origin",f"refs/heads/{self.branch_active}"]):
                    return False
                QMessageBox.information(self, "git", "Pull + push effectués.")
            return True

        # Behind
        if behind > 0:
            message = ("La branche locale est en retard (pull nécessaire).\nVoulez vous effectuer un pull ?")
            if QMessageBox.question(self, "git", message) == QMessageBox.Yes:
                if not self.run_git(["pull", "origin",f"refs/heads/{self.branch_active}"]):
                    return False
                QMessageBox.information(self, "git", "Pull effectué.")
            return True

        # Ahead
        if ahead > 0:
            message = "La branche locale est en avance (push nécessaire).\nVoulez vous effectuer un push ?"
            if QMessageBox.question(self, "git", message) == QMessageBox.Yes:
                if not self.run_git(["push","origin", f"refs/heads/{self.branch_active}"]):
                    return False
                QMessageBox.information(self, "git", "Push effectué.")
            return True

        # À jour
        QMessageBox.information(self, "git", "La branche est à jour.")
        return True

    def on_maj_branch(self):
        # recuperation de l'intitulé du commit
        while True:
            intitule, ok_intitule = QInputDialog.getText(self, "Intitulé du commit", "Intitulé du commit :")
            if not ok_intitule:
                QMessageBox.information(self, "Information", "Mise à jour de la branche annulée")
                return False
            if intitule.strip() == "":
                QMessageBox.warning(self, "Erreur", "L'intitulé ne peut pas être vide")
                continue
            break

        # récuperation des refs aux issues
        text = "Numéros des issues à prendre en compte (séparés par des virgules) :\n\n"
        text += "Exemple : 1,4,12\n"
        issues, ok_issue = QInputDialog.getText(self, "Issues", text)

        if ok_issue:
            type_issue = ["Fixes","Refs"]
            type_issue, ok_type_issue = QInputDialog.getItem(self, "Type de référence", "Type de référence pour les issues :", type_issue, 0, False)
            if not ok_type_issue:
                QMessageBox.information(self, "Information", "Veuillez renseigner le type de référence pour les issues : abandon de la mise à jour de la branche")
                return False
            print("type de référence : ", type_issue)

        # add
        self.run_git(["add", "."])

        # test si commit vide (pas de changements) → abandon du commit et du push
        files = self.get_modified_files()
        if files:
            print(files)
        else:
            QMessageBox.warning(self, "Git", "Aucun changement à commiter, abandon du commit et du push")
            return False

        # commit
        if issues:
            format_issue = ", ".join(f"#{x.strip()}" for x in issues.split(","))
            intitule += f"  ({type_issue}: {format_issue})"

        print("intitulé du commit : ", intitule)

        res = self.run_git(["commit", "-m", intitule])
        if not res:
            return False
        print("commit ok, lancement du push")

        # push
        res = self.run_git(["push","-u","origin", f"refs/heads/{self.branch_active}"])
        if not res:
            return False
        QMessageBox.information(self, "Information", f"Branche mise à jour avec succès :\n {self.branch_active}")
        return True
    def get_branches_distantes(self):
        # listes des branches locales
        res_local = self.run_git(["branch"])
        locales = set()
        if res_local:
            for line in res_local.stdout.splitlines():
                line = line.strip()
                if line.startswith("*"):
                    branch_name = line[2:].strip()
                    locales.add(branch_name)
                else:
                    locales.add(line)
        print("branches locales :", locales)

        # listes des branches distantes
        self.run_git(["fetch", "origin"])
        res_distant = self.run_git(["branch", "-r"])
        distantes = set()
        if res_distant:
            distantes = {
                b.strip().replace("origin/", "")
                for b in res_distant.stdout.splitlines()
                if "->" not in b  # ignore HEAD -> origin/main
            }

        # branches distantes absentes en local
        self.branches_manquantes = sorted(distantes - locales)
        print("branches distantes absentes en local :", self.branches_manquantes)

    def on_maj_branch_from_selected_branch(self):
        if self.selected_branch is None:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une branche.")
            return False

        # fetch
        self.run_git(["fetch","origin"])
        self.run_git(["merge", "--no-ff", f"origin/{self.selected_branch}"], check=False)
        if self.is_conflict():
            fic_conflit = self.get_conflict_files()
            texte = "Conflit détecté sur les fichiers suivants :\n\n"
            for fic in fic_conflit:
                texte += fic + "\n"
            texte += "\nResolvez les conflits manuellement puis faites un add ,commit,push pour finaliser la mise à jour de la branche."
            print("Conflit détecté sur les fichiers suivants :", texte)
            QMessageBox.warning(self, "Conflit détecté", texte)
            return False
        self.on_status_commit()
        return None

    def is_conflict(self):
        res = self.run_git(["diff", "--name-only", "--diff-filter=U"])
        return bool(res.stdout.strip())

    def get_conflict_files(self):
        res = self.run_git(["diff", "--name-only", "--diff-filter=U"])
        if res and res.stdout:
            return res.stdout.strip().splitlines()
        return []

    def on_merge_release(self):
        result = QMessageBox.question(self, "Avertissement", f"Êtes-vous sûr de vouloir faire un merge + tag + release de la branche : {self.branch_active} ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            # =================================
            # merge
            res = self.run_git(["checkout", "main"])
            if not res:
                return False
            res = self.run_git(["pull"])
            if not res:
                return False
            res = self.run_git(["merge", "--no-ff", self.branch_active])
            if not res:
                return False
            res = self.run_git(["push","origin","main"])
            if not res:
                return False

            # =================================
            # TAG BRANCHE (suppression, creation,push)
            tag_name = f"{self.branch_active}_tag"
            # suppr tag local
            self.run_git(["tag", "-d",tag_name],check = False)
            print(tag_name, " : Supprimé (local)")
            # suppr tag distant
            self.run_git(["push", "origin", f":refs/tags/{tag_name}"], check=False)
            print(tag_name," : Supprimé (distant)")

            # creation tag local
            res = self.run_git(["tag", tag_name])
            if not res:
                return False
            print(tag_name, " : crée (local)")
            # push tag local
            res = self.run_git(["push", "origin",tag_name])
            if not res:
                return False
            print(tag_name, " : poussé en distant")

            # =================================
            # TAG version_finale (suppression, creation,push)
            tag_version_finale = "version_finale"

            # suppr tag local
            self.run_git(["tag", "-d", tag_version_finale],check = False)
            print(tag_version_finale, " : Supprimé en local")
            # suppr tag distant
            self.run_git(["push", "origin", f":refs/tags/{tag_version_finale}"], check=False)
            print(tag_version_finale, " : Supprimé en distant")

            # petite attente GitHub (important)
            time.sleep(2)
            # creation tag local
            res = self.run_git(["tag", tag_version_finale])
            if not res:
                return False
            # push tag local
            res = self.run_git(["push", "origin", tag_version_finale])
            if not res:
                return False

            # revenir sur la branche initiale
            if self.run_git(["checkout", self.branch_active]):
                self.refresh_tabwidgets()

            print("Merge + tag + release (workflow) : ", self.branch_active)
            self.refresh_tabwidgets()
            QMessageBox.information(self, "Information","Merge + tag + release (workflow) effectué avec succès :\n"+self.branch_active)
            return True



    def on_suppr_branche(self):
        # if not self.selected_branch:
        #     QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une branche.")
        #     return False
        result = QMessageBox.question(self, "Avertissement", f"Êtes-vous sûr de vouloir supprimer la branche locale et distante : {self.branch_active} ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            if self.branch_active in self.protected:
                QMessageBox.warning(self, "Protection", "Branche protégée : abandon de la suppression")
                return False

            # il faut d'abord se positionner sur une autre branche
            res = self.run_git(["checkout", "main"])
            if not res:
                return False
            # suppression branche distante
            res = self.run_git(["branch", "-D", self.branch_active])
            if not res:
                return False
            res = self.run_git(["push", "origin", "--delete",self.branch_active])
            if not res:
                return False
            print("suppression branche distante : ", self.branch_active)
            self.refresh_tabwidgets()
            QMessageBox.information(self, "Information","Branche locale et distante supprimée :\n"+self.branch_active)
            return True

    def on_branch_double_click(self, item):
        branch_name = item.text()
        if self.run_git(["checkout", branch_name]):
            self.branch_active = branch_name
            self.refresh_tabwidgets()
            QMessageBox.information(self, "Information", f"nouvelle branche active :\n {branch_name}")

    def on_branch_simple_click(self, item):
        branch_name = item.text()
        self.selected_branch = branch_name
        print("branche sélectionnée : ", self.selected_branch)
        text = f"{self.selected_branch} --> {self.branch_active}"
        self.label_maj_from_branche_sel.setText(text)
        self.refresh_tabwidgets()

    def is_valid_branch(self,name):
        return bool(re.match(r"^[a-zA-Z0-9._/-]+$", name))

    def on_create_new_branch(self):
        new_branch_name, ok = QInputDialog.getText(self, "Créer une nouvelle branche", "Donner un nom :")
        if not ok:
            return False
        if not self.is_valid_branch(new_branch_name):
            QMessageBox.critical(self, "Erreur Git",
                                 f"<b><font color='red'>{new_branch_name}</font></b><br>Nom de branche invalide (pas d'espaces ou caractères spéciaux)")
            return False
        print("nouvelle branche = ", new_branch_name )

        # ======================================
        # creation branche locale
        res = self.run_git(["checkout", "-b", new_branch_name])
        if not res:
            QMessageBox.critical(self, "Erreur Git", f"Erreur de : checkout")
            return False

        # ======================================
        # creation et push sur branche distante
        res = self.run_git(["push", "-u","origin", new_branch_name])
        if not res:
            QMessageBox.critical(self, "Erreur Git", f"Erreur de : push")
            return False

        self.refresh_tabwidgets()
        QMessageBox.information(self, "Git", "Branche créée avec succès")
        return True

    def init_dialog(self):
        # branches locales
        branches, self.branch_active = get_all_branch()
        self.tableWidget_branche.setRowCount(len(branches))
        self.tableWidget_branche.setColumnCount(1)

        # branches distantes
        self.tableWidget_branche_distantes.setRowCount(len(self.branches_manquantes))
        self.tableWidget_branche_distantes.setColumnCount(1)


        self.label_status.setStyleSheet("color:red; font-weight:bold;")
        self.label_status_commit.setStyleSheet("color:red; font-weight:bold;")
        self.label_maj_branche.setStyleSheet("color:red; font-weight:bold;")
        self.label_maj_from_branche_sel.setStyleSheet("color:blue; font-weight:bold;")
        self.label_suppr_branche.setStyleSheet("color:red; font-weight:bold;")
        self.label_merge_release.setStyleSheet("color:red; font-weight:bold;")

        self.label_status.setText(self.branch_active)
        self.label_status_commit.setText(self.branch_active)
        self.label_maj_branche.setText(self.branch_active)
        self.label_maj_from_branche_sel.setText("")
        self.label_suppr_branche.setText(self.branch_active)
        self.label_merge_release.setText(self.branch_active)

        # branches locales
        for i, branch in enumerate(branches):
            item = QTableWidgetItem(branch)
            if branch == self.branch_active:
                item.setBackground(QColor("lightgreen"))
            self.tableWidget_branche.setItem(i, 0, item)
        self.tableWidget_branche.resizeRowsToContents()

        # branches distantes absentes en local
        for i, branch in enumerate(self.branches_manquantes):
            item = QTableWidgetItem(branch)
            self.tableWidget_branche_distantes.setItem(i, 0, item)
        self.tableWidget_branche_distantes.resizeRowsToContents()

        self.exec()

    def refresh_tabwidgets(self):
        branches, current = get_all_branch()
        table = self.tableWidget_branche
        table.setRowCount(len(branches))
        for i, branch in enumerate(branches):
            item = QTableWidgetItem(branch)
            if branch == current:
                item.setBackground(QColor("lightgreen"))
            table.setItem(i, 0, item)

        self.branch_active = current

        self.label_status.setText(self.branch_active)
        self.label_status_commit.setText(self.branch_active)
        self.label_maj_branche.setText(self.branch_active)
        self.label_suppr_branche.setText(self.branch_active)
        self.label_merge_release.setText(self.branch_active)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dlg = GitManagerDialog()

    dlg.get_branches_distantes()

    # get_version()
    dlg.init_dialog()
