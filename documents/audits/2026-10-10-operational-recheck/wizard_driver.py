import json, os, time, traceback
from pathlib import Path
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QPushButton, QApplication, QDialog, QLabel
from PyQt6.QtTest import QTest
run=Path(os.environ['HELIX_TRIAL_RUN'])
def record(**kw):
    with (run/'wizard-ui.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),**kw})+'\n')
def attach(window):
    seen=set(); last_status=[None]; closing=[False]
    def tick():
        try:
            status={'page':window.page_stack.currentIndex(),'install_rc':getattr(window,'_install_rc',None),'status':window.statusBar().currentMessage(),'child_pid':getattr(getattr(window,'_agent_process',None),'pid',None)}
            if status!=last_status[0]:
                record(event='status',**status);last_status[0]=status
                window.grab().save(str(run/'screenshots'/('status-'+str(time.time_ns())+'.png')))
                for w in QApplication.topLevelWidgets():
                    if isinstance(w,QDialog) and w.isVisible():w.grab().save(str(run/'screenshots'/('dialog-'+str(time.time_ns())+'.png')))
            if (run/'close-wizard').exists():
                if not closing[0]:record(event='close_requested');closing[0]=True;window.close()
                return
            if window.dashboard_widget is not None:return
            i=window.page_stack.currentIndex()
            if i in seen:return
            page=window.pages[i]
            if i==1:
                page.provider_combo.setCurrentText('Ollama (Local)')
                page.model_combo.setCurrentText('granite4.1:3b')
                page.ollama_url.setText('http://127.0.0.1:11434')
                page.telegram_check.setChecked(False);page.discord_check.setChecked(False)
            if i==2:
                page.agent_name.setText('Helix');page.creator_name.setText('Joshua')
            if i==3:
                for name,check in page.checks.items():
                    if check.isEnabled():check.setChecked(name in ('core','files'))
                record(event='selected_tools',tools=[k for k,v in page.checks.items() if v.isChecked()])
            if i==4:page.safety_check.setChecked(True)
            if i==6:
                page.shortcut_wizard_chk.setChecked(False);page.shortcut_agent_chk.setChecked(False)
                button=page.launch_btn
            else:
                button=next(b for b in page.findChildren(QPushButton) if b.text().startswith(('Next','Get Started')))
            window.grab().save(str(run/'screenshots'/f'page-{i}.png'))
            record(event='click',page=i,button=button.text());seen.add(i)
            QTest.mouseClick(button,Qt.MouseButton.LeftButton)
        except Exception:record(event='driver_error',error=traceback.format_exc());timer.stop()
    timer=QTimer(window);timer.timeout.connect(tick);timer.start(1000);window._trial_ui_timer=timer
