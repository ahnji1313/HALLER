use std::fs;
use std::path::Path;

use anyhow::{anyhow, Context, Result};
use log::info;
use pyo3::exceptions::PyAttributeError;
use pyo3::prelude::*;

struct ScriptHooks {
    module_name: String,
    on_frame_begin: Option<PyObject>,
    on_update: Option<PyObject>,
}

pub struct ScriptHost {
    scripts: Vec<ScriptHooks>,
}

impl ScriptHost {
    pub fn new(scripts_dir: &Path) -> Result<Self> {
        let mut sources = Vec::new();

        if scripts_dir.exists() {
            for entry in fs::read_dir(scripts_dir).context("failed to read scripts directory")? {
                let entry = entry.context("failed to read directory entry")?;
                let path = entry.path();
                if is_python_file(&path) {
                    let module_name = path
                        .file_stem()
                        .and_then(|stem| stem.to_str())
                        .unwrap_or("script")
                        .to_string();
                    let source = fs::read_to_string(&path).with_context(|| {
                        format!("failed to read script source for {}", module_name)
                    })?;
                    sources.push((module_name, source, path));
                }
            }
        }

        let scripts = Python::with_gil(|py| -> PyResult<Vec<ScriptHooks>> {
            let mut compiled = Vec::new();

            for (module_name, source, path) in &sources {
                let module =
                    PyModule::from_code(py, source, path.to_string_lossy().as_ref(), module_name)?;

                let on_frame_begin = match module.getattr("on_frame_begin") {
                    Ok(callback) => Some(callback.into_py(py)),
                    Err(err) => {
                        if err.is_instance_of::<PyAttributeError>(py) {
                            None
                        } else {
                            return Err(err);
                        }
                    }
                };

                let on_update = match module.getattr("on_update") {
                    Ok(callback) => Some(callback.into_py(py)),
                    Err(err) => {
                        if err.is_instance_of::<PyAttributeError>(py) {
                            None
                        } else {
                            return Err(err);
                        }
                    }
                };

                compiled.push(ScriptHooks {
                    module_name: module_name.clone(),
                    on_frame_begin,
                    on_update,
                });
            }

            Ok(compiled)
        })?;

        if !scripts.is_empty() {
            info!("Loaded {} script(s) for Envision Engine", scripts.len());
        }

        Ok(Self { scripts })
    }

    pub fn notify_frame_begin(&self) -> Result<()> {
        Python::with_gil(|py| -> PyResult<()> {
            for script in &self.scripts {
                if let Some(callback) = &script.on_frame_begin {
                    callback.call0(py)?;
                }
            }
            Ok(())
        })
        .map_err(|err| anyhow!("script hook on_frame_begin failed: {err}"))
    }

    pub fn notify_update(&mut self, delta_seconds: f64) -> Result<()> {
        Python::with_gil(|py| -> PyResult<()> {
            for script in &self.scripts {
                if let Some(callback) = &script.on_update {
                    callback.call1(py, (delta_seconds,))?;
                }
            }
            Ok(())
        })
        .map_err(|err| anyhow!("script hook on_update failed: {err}"))
    }
}

fn is_python_file(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.eq_ignore_ascii_case("py"))
        .unwrap_or(false)
}
