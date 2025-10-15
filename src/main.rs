use std::path::Path;
use std::time::Instant;

use anyhow::Context;
use envision_gpu_core::gpu_core::{GpuCore, RenderParams};
use envision_gpu_core::script_host::ScriptHost;
use log::{error, info};
use winit::event::{Event, WindowEvent};
use winit::event_loop::{ControlFlow, EventLoop};
use winit::window::WindowBuilder;

slint::include_modules!();

fn main() -> anyhow::Result<()> {
    env_logger::init();

    let main_window = MainWindow::new().context("failed to initialize Slint main window")?;
    main_window.window().set_title("Envision Engine Prototype");
    main_window
        .show()
        .context("failed to show Slint main window")?;
    let main_window_handle = main_window.as_weak();

    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("Envision Engine Render Surface")
        .build(&event_loop)
        .context("failed to create Winit window for renderer")?;

    let instance = wgpu::Instance::default();
    let surface = unsafe { instance.create_surface(&window) }
        .context("failed to create WGPU surface for render window")?;

    let mut gpu_core = GpuCore::initialize().context("failed to initialize GPU core")?;
    let mut script_host = ScriptHost::new(Path::new("scripts"))?;

    let mut accumulated_time = 0.0f32;
    let mut last_frame = Instant::now();

    info!("Starting Envision Engine render loop");

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Poll;

        match event {
            Event::WindowEvent {
                event: WindowEvent::CloseRequested,
                ..
            } => {
                *control_flow = ControlFlow::Exit;
            }
            Event::MainEventsCleared => {
                let elapsed = last_frame.elapsed();
                last_frame = Instant::now();
                let delta_seconds = elapsed.as_secs_f64();
                accumulated_time += delta_seconds as f32;

                if let Err(err) = script_host.notify_frame_begin() {
                    error!("Python on_frame_begin hook error: {err}");
                }

                if let Err(err) = script_host.notify_update(delta_seconds) {
                    error!("Python on_update hook error: {err}");
                }

                let render_params = RenderParams {
                    time: accumulated_time,
                    ..RenderParams::default()
                };

                if let Err(err) = gpu_core.render_frame(render_params) {
                    error!("GPU render_frame error: {err}");
                }

                if let Some(main_window) = main_window_handle.upgrade() {
                    main_window.window().request_redraw();
                }
                window.request_redraw();
            }
            Event::RedrawRequested(_) => {
                // TODO: Integrate swapchain presentation to the WGPU surface.
                let _ = &surface;
            }
            _ => {}
        }
        let _ = &main_window;
    });
}
