import os

class FileReader:
    """
    ファイルを読み込むクラス。
    """

    def find_file_list(self, search_dir: str) -> list[str]:
        """
        指定したディレクトリ内のファイル名のリストを返す。
        """
        # モジュールファイルの親ディレクトリ
        repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 検索対象のディレクトリを決定する
        if not search_dir:
            search_dir = repo_path
        else:
            search_dir = os.path.join(repo_path, search_dir)

        # 指定したディレクトリ直下に存在するファイル名のリストを取得する
        # サブディレクトリ以下や.DS_Storeなどの隠しファイルは除く
        file_list = []
        for file in os.listdir(search_dir):
            if not file.startswith('.') and os.path.isfile(os.path.join(search_dir, file)):
                file_list.append(file)
        
        return file_list


    def find_file_path(self, file_name: str, search_dir: str = "") -> str:
        """
        指定したディレクトリ内で、指定したファイル名を持つファイルのパスを返す。
        該当するファイルがない場合は、空文字列を返す。
        """
        # モジュールファイルの親ディレクトリ
        repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 検索対象のディレクトリを決定する
        if not search_dir:
            search_dir = repo_path
        else:
            search_dir = os.path.join(repo_path, search_dir)

        # 指定されたディレクトリ内でファイルを探索する
        for root, dirs, files in os.walk(search_dir):
            if file_name in files:
                return os.path.join(root, file_name)
        raise FileNotFoundError(f"{file_name}が見つかりませんでした。")



    def read_file(self, file_name: str, search_dir: str = "") -> str:
        """
        指定したファイル名の中身を文字列として返す。
        該当するファイルがない場合は、空文字列を返す。
        """

        file_path = self.find_file_path(file_name, search_dir)

        # 該当するファイルがなかった場合は、空文字列を返す
        if not file_path:
            return ""

        # 該当するファイルがあった場合は、UTF-8エンコードでファイルを開いて中身を返す
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
