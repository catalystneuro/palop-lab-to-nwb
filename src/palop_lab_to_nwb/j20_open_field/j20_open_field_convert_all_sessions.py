import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from palop_lab_to_nwb.j20_open_field.j20_open_field_convert_session import get_sessions, session_to_nwb


def safe_session_to_nwb(*, exception_file_path: Path, **session_to_nwb_kwargs):
    try:
        session_to_nwb(**session_to_nwb_kwargs)
    except Exception:
        exception_file_path.write_text(traceback.format_exc())


def dataset_to_nwb(
    data_dir_path: str | Path,
    output_dir_path: str | Path,
    max_workers: int = 1,
    stub_test: bool = False,
    overwrite: bool = False,
):
    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    exception_dir_path = output_dir_path / "exceptions"
    exception_dir_path.mkdir(parents=True, exist_ok=True)

    session_ids = get_sessions(data_dir_path).index.tolist()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                safe_session_to_nwb,
                data_dir_path=data_dir_path,
                output_dir_path=output_dir_path,
                session_id=session_id,
                stub_test=stub_test,
                overwrite=overwrite,
                exception_file_path=exception_dir_path / f"{session_id}.txt",
            )
            for session_id in session_ids
        ]
        for future in tqdm(as_completed(futures), total=len(futures)):
            future.result()


if __name__ == "__main__":
    dataset_to_nwb(
        data_dir_path="/Volumes/seagate_0/vame/J20",
        output_dir_path=Path("~/conversion_nwb/palop-lab-to-nwb").expanduser(),
        max_workers=4,
        stub_test=False,
        overwrite=True,
    )
