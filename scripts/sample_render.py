"""Sample script demonstrating how to call the Envision GPU Core from Python."""

import envision_gpu_core as gpu_core


def main() -> None:
    """Initialize the GPU core and render a stub frame."""
    gpu_core.initialize()
    gpu_core.render_frame(
        target_label="sample-frame",
        width=1280,
        height=720,
        time=0.0,
        layers=[],
    )
    print("Envision GPU Core render_frame executed successfully.")


if __name__ == "__main__":
    main()
