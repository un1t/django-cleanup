def sorl_delete(file_):
    try:
        from sorl.thumbnail import delete
        delete(file_, delete_file=False)
    except ImportError:
        pass
