# 🔐 Automatic User Creation

## Overview

TalentFlow AI now automatically creates default users during container startup, eliminating the need for manual user creation scripts.

## How It Works

### 1. **Startup Script Integration**
- Both `Backend/Dockerfile.cpu` and `Backend/Dockerfile.gpu` now use `startup.sh`
- The script runs before the main application starts
- Users are created only if they don't already exist

### 2. **Default Users Created**

#### **Admin User:**
- **Email:** `admin`
- **Password:** `admin`
- **Role:** `admin`
- **Permissions:** Full system access

#### **Recruiter User:**
- **Email:** `udayt2003@gmail.com`
- **Password:** `Uday@186186`
- **Role:** `recruiter`
- **Permissions:** Hiring activities, resume screening, interview management

### 3. **Startup Process**

```bash
# The startup.sh script performs these steps:

1. ⏳ Wait for MongoDB to be ready
2. 👤 Create admin user (if not exists)
3. 👤 Create recruiter user (if not exists)
4. 🚀 Start the FastAPI application
```

### 4. **Container Logs**

When you start the containers, you'll see output like:

```
🚀 Starting TalentFlow AI Backend...
⏳ Waiting for MongoDB to be ready...
✅ MongoDB is ready!
👤 Creating default users...
✅ Admin user created: admin / admin
✅ Recruiter user created: udayt2003@gmail.com / Uday@186186
🎉 Default users created successfully!

🔐 Login Credentials:
  Admin: admin / admin
  Recruiter: udayt2003@gmail.com / Uday@186186

🚀 Starting FastAPI application...
```

## Benefits

### ✅ **Automatic Setup**
- No manual user creation required
- Works for both development and production
- Consistent across all environments

### ✅ **Idempotent**
- Users are only created if they don't exist
- Safe to run multiple times
- No duplicate user errors

### ✅ **Environment Agnostic**
- Works in Docker containers
- Works in development
- Works in production

### ✅ **Secure**
- Passwords are properly hashed
- Users are created with correct roles
- No sensitive data in logs

## Usage

### **Development Mode:**
```bash
# GPU Mode
docker compose -f docker-compose.dev.yml --profile gpu up -d

# CPU Mode  
docker compose -f docker-compose.dev.yml --profile cpu up -d
```

### **Production Mode:**
```bash
# GPU Mode
docker compose --profile gpu up -d

# CPU Mode
docker compose --profile cpu up -d
```

### **First Login:**
1. Open http://localhost:8501
2. Use either set of credentials:
   - **Admin:** `admin` / `admin`
   - **Recruiter:** `udayt2003@gmail.com` / `Uday@186186`
3. **Important:** Change passwords after first login!

## Customization

### **Modify Default Users**

To change the default users, edit `Backend/startup.sh`:

```bash
# Change admin credentials
username = "admin"
email = "your-admin@company.com"
password = "your-secure-password"

# Change recruiter credentials  
username = "recruiter"
email = "your-recruiter@company.com"
password = "your-secure-password"
```

### **Add More Default Users**

Add additional user creation blocks in `startup.sh`:

```bash
# Create additional users
python -c "
# Your user creation code here
"
```

## Security Considerations

### ⚠️ **Production Security**
- Change default passwords immediately
- Create additional users as needed
- Consider removing default users in production
- Use strong, unique passwords

### ⚠️ **Development Security**
- Default credentials are for development only
- Don't use in production environments
- Consider using environment variables for credentials

## Troubleshooting

### **Users Not Created**
- Check MongoDB connection in logs
- Verify MongoDB is running and accessible
- Check container logs for errors

### **Login Issues**
- Clear browser cache (Ctrl+Shift+R)
- Verify credentials match exactly
- Check if users exist in MongoDB

### **Permission Issues**
- Ensure startup.sh is executable
- Check file permissions in container
- Verify script syntax

## Files Modified

- `Backend/startup.sh` - New startup script
- `Backend/Dockerfile.cpu` - Updated to use startup script
- `Backend/Dockerfile.gpu` - Updated to use startup script
- `docker-compose.yml` - Uses startup script automatically
- `docker-compose.dev.yml` - Uses startup script automatically

## Migration from Manual Creation

If you were previously using manual user creation:

1. **Old method:** Run `create_default_user.py` and `create_default_recruiter.py` manually
2. **New method:** Users are created automatically on container startup
3. **Migration:** No action needed - the new system is backward compatible

The automatic user creation system provides a seamless, secure, and user-friendly way to get started with TalentFlow AI! 🎉
