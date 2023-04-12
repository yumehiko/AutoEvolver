import subprocess


class ModuleRunner:
    """
    指定したモジュールを実行するクラス。
    """
    def run_module(self, module_name: str, directory: str) -> None:
        """
        指定したモジュールを実行する。
        """
        subprocess.run(["python", "-m", module_name], cwd=directory)

