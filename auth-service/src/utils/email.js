const nodemailer = require('nodemailer');

const createTransport = () => {
  if (process.env.DISABLE_EMAIL === 'true') {
    return { sendMail: (opts) => { console.log('Email disabled - would send:', opts); return Promise.resolve(); } };
  }
  const transporter = nodemailer.createTransport({
    host: process.env.EMAIL_HOST,
    port: parseInt(process.env.EMAIL_PORT || '587', 10),
    secure: process.env.EMAIL_SECURE === 'true',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
  return transporter;
};

const sendOtpEmail = async (to, otp) => {
  const transporter = createTransport();
  const mail = {
    from: process.env.EMAIL_FROM,
    to,
    subject: 'Your Athena verification code',
    html: `<p>Your verification code is <b>${otp}</b>. It expires in ${process.env.OTP_TTL_MINUTES || 10} minutes.</p>`
  };
  return transporter.sendMail(mail);
};

module.exports = { sendOtpEmail };
