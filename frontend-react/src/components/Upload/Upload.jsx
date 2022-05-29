import React from 'react';
import './style.scss';

const styles = {
    uploadProgress: {
        current: {
            marginLeft: '-45px',
            position: 'absolute',
            textAlign: 'right',
            width: '40px',
        },
        summary: {
            marginLeft: '5px',
            position: 'absolute',
        },
    },
    popup: {
        common: {
            width: '270px',
            textAlign: 'center',
        },
        hints: {
            heading: {
                fontSize: '13px',
            },
            outgoing: {
                marginTop: '30px',
                display: 'flex',
                justifyContent: 'space-between',
                marginLeft: '15px',
                marginRight: '15px',
                borderBottom: '1px solid #cacaca',
                paddingBottom: '5px',
            },
            incomming: {
                display: 'flex',
                justifyContent: 'space-between',
                marginLeft: '15px',
                marginRight: '15px',
                paddingTop: '5px',
                marginBottom: '60px',
            },
        },
    },
};

const Upload = () => (
    <React.Fragment>
        <div id='upload' className='button'>
            Загрузить звонки
        </div>
        <div className='popup' id='progress'>
            <span className='icon-Updating'>
                <span className='path1' />
                <span className='path2' />
            </span>
            <span className='text'>
                <span id='current-upload' style={styles.uploadProgress.current} />
                <span id='separator'>/</span>
                <span id='summary-upload' style={styles.uploadProgress.summary} />
            </span>
        </div>
        <div className='popup' id='dialog'>
            <div style={styles.popup.common}>
                <p>Укажите направление звонка</p>
                <span style={styles.popup.hints.heading}>
                    Это важно для правильного определения менеджера и клиента в разговоре
                </span>
                <div style={styles.popup.hints.outgoing}>
                    <span>Исходящие звонки</span>
                    <input type='radio' name='type' value='False' defaultChecked />
                </div>
                <div style={styles.popup.hints.incomming}>
                    <span>Входящие звонки</span>
                    <input type='radio' name='type' value='True' />
                </div>
                <div className='call-stats-element-row'>
                    <button type='submit' className='button'>
                        Установить
                    </button>
                    <div className='button'>Отмена</div>
                </div>
            </div>
        </div>
    </React.Fragment>
);
export default Upload;
